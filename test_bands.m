function [] = test_bands(path)
% This function runs the image at 'path' through the trained model and 
% displays the result
%% Args:
% path: Full path to image to be analysed

clc
close all
%% Dimensions of segments and criteria for flatness

block_column=50;block_row=30;
flatness_criteria=0.5;
%% Load the image file and store in matrix

im_mat = [];
div_mat=[];
image1 = imread(path);
image_g=rgb2gray(image1);
[divided_img,Lcolumn,Lrow]=divideIntoBlocks_final(image_g,block_row,block_column);
divisions=Lcolumn*Lrow;
div_mat=[div_mat; divisions Lrow Lcolumn];

for count=1:divisions
    imgg=divided_img(:,:,count);
    image_vec=imgg(:);
    im_mat=[im_mat;image_vec'];
end
clear image image_g image_vec lst fil fil1 lst1 divided_img num Lcolumn Lrow divisions

%% Pass loaded images through the model

% Averaging over the chosen models in the loaded network
load chosen_net_skewed_1_5000.mat;
for i=1:length(chosen_indices)
    neti=selected_net_skewed{i};
    outi(:,:,i)=neti(im_mat');
end
out=sum(outi,3)/size(outi,3);    

% Decide if image contains a flat band based on flatness crieteria
if max(out(2,1:div_mat(1,1))) > flatness_criteria
    pred=1;    
end

%% Visualize the output and bands
% Red box shows segments with predicted flat bands

figure(4)
for j=1:div_mat(1,1)
    H=subplot(div_mat(1,2),div_mat(1,3),j);
    imshow(uint8(reshape(im_mat(j,:),block_row,block_column)));
    if out(2,j) > flatness_criteria
        text(10,-10,string(out(2,j)));
        set(H,'box','on','Visible','on','LineWidth',2,'XColor','red','YColor','red','xtick',[],'ytick',[]);
    end
end
if pred==1
    title(["Material has flat bands"]);
elseif pred==0
    title(["Material does not have flat bands"]);
end
waiting; 
close(figure(4));

