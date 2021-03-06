import numpy as np
from sklearn.cluster import KMeans
from scipy import misc
import sys, os

TRANSPARENT = (u"\\U00002601", "https://static.xx.fbcdn.net/images/emoji.php/v8/zf4/1/32/2601.png")

def flatten_image(image, transparent=False):
    n = image.shape[0] * image.shape[1]
    if transparent and image.shape[2]==4:
        pixels = np.zeros((n, 4))
        pixels[:,0] = np.ndarray.flatten(image[:,:,0])
        pixels[:,1] = np.ndarray.flatten(image[:,:,1])
        pixels[:,2] = np.ndarray.flatten(image[:,:,2])
        pixels[:,3] = np.ndarray.flatten(image[:,:,3])
    else:
        pixels = np.zeros((n, 3))
        pixels[:,0] = np.ndarray.flatten(image[:,:,0])
        pixels[:,1] = np.ndarray.flatten(image[:,:,1])
        pixels[:,2] = np.ndarray.flatten(image[:,:,2])
    return pixels

def cluster_pixels(pixels, k=10):
    n = pixels.shape[0]

    kmeans = KMeans(n_clusters=int(k)).fit(pixels)
    assignment = kmeans.labels_
    centroid = kmeans.cluster_centers_

    return assignment, centroid

def assign_emoji_to_cluster(cluster_centroids, emoji_color, emoji_character):
    distance = np.zeros(emoji_color.shape[0])
    assigned_emoji = []
    # print cluster_centroids
    for i in range(cluster_centroids.shape[0]):
        distance = np.linalg.norm(cluster_centroids[i,:] - emoji_color, axis=1)
        # print(distance)
        emoji_index = np.argmin(distance)
        assigned_emoji.append(emoji_character[emoji_index])
    # print(assigned_emoji)
    return assigned_emoji

def reconstruct_image(assigned_emoji, original_image, assignment):
    rows = original_image.shape[0]
    cols = original_image.shape[1]
    new_image = []
    flat_image = flatten_image(original_image, transparent=True)
    for i in range(rows*cols):
        if flat_image.shape[1]==4 and flat_image[i,3] == 0:
            new_image.append(TRANSPARENT)
        else:
            new_image.append(assigned_emoji[assignment[i]])
    # print new_image
    out_image = []
    for i in range(rows):
        out_image.append(new_image[i*cols: i*cols+cols])
    return out_image

def convert_image_to_emoji(filename, emoji_color, emoji_character, k=5, width=75):
    image = misc.imread(filename)
    rows = image.shape[0]
    cols = image.shape[1]
    height = (rows*width)/cols
    image = misc.imresize(image, (height, width))
    flattened_image = flatten_image(image)
    assignment, centroids = cluster_pixels(flattened_image, k=k)
    assigned_emoji = assign_emoji_to_cluster(centroids, emoji_color, emoji_character)
    new_image = reconstruct_image(assigned_emoji, image, assignment)
    out_text = []

    for row in new_image:
        out_text.append([(character.decode('unicode-escape'), url) for character, url in row])
    # print out_text
    return out_text, (height, width)

if __name__ == '__main__':
    convert_image_to_emoji(sys.argv[1], sys.argv[2], sys.argv[3])
