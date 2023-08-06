import setuptools

with open("./kmeans_sam/README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='kmeans_sam',  
     version='0.1.4',
     author="Nishant Nischaya",
     author_email="nishantnischaya@gmail.com",
     description="A package for creating subclusters of KMeansSam clusters and merging them with great flexibility",
     long_description=long_description,
     keywords=['k-means', 'sub-clustering', 'Merging', 'clustering', 'clusters', 'Machine Learning', 'Data Science', 'Python3'],
    long_description_content_type="text/markdown",
     url="https://github.com/nishantnischaya/k-means-sam",
     packages=setuptools.find_packages(),
     classifiers=[
         "Development Status :: 3 - Alpha",
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )