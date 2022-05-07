#Program to access bandstructures from Materials Project, 2DMatpedia, or Aflow and run them through Anupam's
#trained model to test if it contains flat bands.

from sys import excepthook
import numpy as np
import json

from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine
from pymatgen.electronic_structure.plotter import BSPlotter
from plotting_func import plotting_function

from aflow import *
import lzma

from tkinter import *
from tkinter import simpledialog
from tkinter import ttk
     
def MatProj(materialID):

    """
    Accesses specified Materials Project material's bandstructure data from the API and saves a plot of it

    Args:
        materialID (float): User selected Materials Project Material ID to access

    Returns:
        Path to where the bandstructure is saved
    """

    from pymatgen.ext.matproj import MPRester
    myKey = 'eFInA76SG5V2i0lp'
    with MPRester(myKey) as mpr:
        name = "mp-"+str(materialID)
        try:
            bands = mpr.get_bandstructure_by_material_id(name)
        except:
            return "void"
        if bands == None:
            return "void"
        bsplot = BSPlotter(bands)
        data = bsplot.bs_plot_data()
        distances, energies = data["distances"], data["energy"]["1"]

        k_gaps = count_arrays_over_one(data["distances"])
        distances = _rescale_distances_evenly(distances)

        plot = plotting_function(distances, energies, k_gaps, 3)
        path = "./Materials Project/"+ name + ".png"
        plot.savefig(path ,dpi=50)
        print("Done")

        return path

def TwoDMatpedia(materialID):

    """
    Accesses specified 2D Matpedia material's bandstructure data from a saved file and saves a plot of it

    Args:
        materialID (float): User selected 2D Matpedia Material ID to access

    Returns:
        Path to where the bandstructure is saved
    """

    bands_path = r'/Users/olwynread/Documents/Work/Project/2DMatpedia/2dmatpedia_band.json/bands/'
    #Haven't found a way to access individual materials on 2DMatpedia so the files have to be downloaded first
    #and saved to the above path
    name = "2dm-"+str(materialID)
    file = name + ".json"
    try:
        bands_dict=json.load(open(bands_path+file))
    except:
        return "void"
    bands=BandStructureSymmLine.from_dict(bands_dict)
    bsplot = BSPlotter(bands)
    data = bsplot.bs_plot_data()
    distances, energies = data["distances"], data["energy"]["1"]

    k_gaps = count_arrays_over_one(data["distances"])
    distances = _rescale_distances_evenly(distances)

    plot = plotting_function(distances, energies, k_gaps, 2.5)
    path = "./2DMatpedia/" + name + "NEW.png"
    plot.savefig(path ,dpi=50)
    print("Done")

    return path

def Aflow(materialID):

    """
    Accesses specified Aflow material's bandstructure data from the API and saves a plot of it

    Args:
        materialID (float): User selected Aflow Material ID to access

    Returns:
        Path to where the bandstructure is saved.
    """

    result = search(catalog= 'icsd').select(K.auid == materialID )
    try:
        a0 = result[0]
    except:
        return "void"
    a0.files["*bandsdata.json.xz"](materialID+".json.xz")
    lzma.open(filename= materialID+".json.xz")

    with open(materialID+".json.xz", mode= 'rb') as compressed, \
        open(materialID+".json", 'wb') as out:
        data = compressed.read()
        data = lzma.decompress(data)
        out.write(data)

    bands = json.load(open("./"+materialID+".json"))

    try:
        distances, energies = Aflow_data_for_plot(bands, "bands_data")
        k_gaps = count_arrays_over_one(distances)
        distances = _rescale_distances_evenly(distances)
    except:
        #Deals with materials which have seperate spin up and spin down bands
        maj_distances, maj_energies = Aflow_data_for_plot(bands, "bands_data_majority")
        min_distances, min_energies = Aflow_data_for_plot(bands, "bands_data_minority")
        energies = maj_energies + min_energies
        maj_distances = _rescale_distances_evenly(maj_distances)
        min_distances = _rescale_distances_evenly(min_distances)
        distances = maj_distances + min_distances
        k_gaps = count_arrays_over_one(distances)/2
            
    plot = plotting_function(distances, energies, k_gaps, 3, Aflow = True)
    path = "./Aflow/"+ materialID + ".png"
    plot.savefig(path ,dpi=50)
    print("Done")

    return path

def Aflow_data_for_plot(bandsdata, label):
    
    """
    Method for formatting Aflow bandstructure data for plotting

    Args:
        bandsdata (dict): Dict of bandstructure data, including distances, energies, and k-point information
        label (string): Key to access the required data
    Returns:
        distances: Correctly formatted distances
        energies: Correctly formatted energies.
    """

    k = 0
    i = 0
    distances = []
    energies = []
    TempD = []
    TempE = []

    for length in range(len(bandsdata[label])):
        tempE = []
        for j in range(len(bandsdata[label][length])):            
            if j == 0:
                TempD.append(bandsdata[label][length][j])
            else:
                tempE.append(bandsdata[label][length][j])
        TempE.append(np.array(tempE))
        i += 1 
        if bandsdata[label][length][0] == bandsdata["kpoint_positions"][k+1]:
            distances.append(np.array(TempD))
            energies.append(np.array(TempE))
            TempD = []
            TempE = []
            k += 1
            i = 0
            
    return distances, energies

def count_arrays_over_one(dict):

    """
    Method for counting the number of entries in a dictionary with a length greater than 1.
    Required as some k-point gaps are single points and need to not be counted.
    """

    count = 0
    for j in dict:
        if len(j) > 1:
            count += 1
        else:
            continue

    return count

def _rescale_distances_evenly(distances):

    """
    Method to rescale distances of bs so that there is equal distance (1) between K points.
    """ 

    scaled_distances = []
    av_distance_per_branch = 1
    base_distance = 0

    for br in distances:
        distance_holder = []
        num_gaps = len(br)-1
        if num_gaps == 0:
            #incase of 0 point branches
            dist_per_gap = 0
            distance_holder.extend([base_distance])
        else:
            dist_per_gap = av_distance_per_branch/num_gaps
            distance_holder.extend([base_distance + i*dist_per_gap for i in range(num_gaps+1)])                  
        base_distance += num_gaps*dist_per_gap
        scaled_distances.append(np.array(distance_holder))

    return scaled_distances
    
def run_on_model(path):

    """
    Method to run the image at path through the model on MatLab
    """

    import matlab.engine
    eng = matlab.engine.start_matlab()
    eng.test_bands(path, nargout=0)
    eng.quit()


for i in range(5723, 6461):
    TwoDMatpedia(i)



#Added a basic GUI for ease of use

win = Tk()
win.title("Select database")
win.geometry("200x100")

button_dict={}
option= ["Materials Project", "2D Matpedia", "Aflow"]

for i in option:
    def func(x=i):
        if x == "Materials Project":
            material_id = simpledialog.askstring(title="Test", prompt="Enter Materials Project ID (for mp-123 enter 123):")
            win.destroy()
            path = MatProj(material_id)
            if path == "void":
                print(path)
            else:
                run_on_model(path)

        elif x == "2D Matpedia":
            material_id = simpledialog.askstring(title="Test", prompt="Enter 2DMatpedia ID (for 2dm-123 enter 123):")
            win.destroy()
            path = TwoDMatpedia(material_id)
            if path =="void":
                print(path)
            else:
                run_on_model(path)

        elif x == "Aflow":
            material_id = simpledialog.askstring(title="Test", prompt="Enter Aflow AUID (of the form aflow:dddf72b887a54b04):")
            win.destroy()
            path = Aflow(material_id)
            if path =="void":
                print(path)
            else:
                run_on_model(path)

    button_dict[i]=ttk.Button(win, text=i, command= func)
    button_dict[i].pack()

win.mainloop()
