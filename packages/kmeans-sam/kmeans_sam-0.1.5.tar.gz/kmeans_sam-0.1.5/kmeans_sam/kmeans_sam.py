import pandas
import numpy as np

class KMeansSam():
    def __init__(self):
        self.__map_df = {}
    
    def clusterize(self, model, df: pandas.DataFrame, predictors: list) -> map:
        """
        Make clusters from dataframe using kmeans clustering
        """
        labels = model.predict(df[predictors])
        df['cluster'] = labels
        for i in range(model.n_clusters):
            self.__map_df[i] = df[df['cluster'] == i]
        return self.__map_df

    def get_cluster(self, cluster_id: int) -> pandas.DataFrame:
        """
        Get cluster by id
        """
        return self.__map_df[cluster_id]

    def get_all_clusters(self) -> map:
        return self.__map_df

    def merge_cluster(self, cluster_ids: list) -> pandas.DataFrame:
        """
        Merge clusters by list of cluster ids
        """
        df = pandas.DataFrame()
        # vectorize get_cluster function
        get_cluster_vector = np.vectorize(self.get_cluster, otypes=[object])

        df = pandas.concat(get_cluster_vector(cluster_ids))
        [self.__map_df.pop(key) for key in cluster_ids]
        self.__map_df = self.__rearrange_map(self.__map_df)

        # largest key in map_df is the last cluster
        last_cluster_id = max(self.__map_df.keys())
        df.drop(columns=['cluster'], inplace=True)
        df['cluster'] = last_cluster_id + 1
        self.__map_df[last_cluster_id + 1] = df
        return self.__map_df[last_cluster_id + 1]

    def __rearrange_map(self, map_df: map) -> map:
        """
        Rearrange map to make indices countinuous starting from 0
        """
        new_map = {}
        i = 0
        for key in map_df:
            map_df[key].drop(columns=['cluster'], inplace=True)
            map_df[key]['cluster'] = i
            new_map[i] = map_df[key]
            i += 1
        return new_map

    def subclusterize(self, model, cluster_id: int, predictors: list) -> map:
        """
        Subclusterize cluster by cluster id using kmeans clustering
        """
        df = self.get_cluster(cluster_id)
        labels = model.predict(df[predictors])
        df.drop(columns=['cluster'], inplace=True)
        df['cluster'] = labels
        for i in range(model.n_clusters):
            if i == 0:
                self.__map_df[cluster_id] = df[df['cluster'] == i]
            else:
                self.__map_df[model.n_clusters + i] = df[df['cluster'] == i]
        self.__map_df = self.__rearrange_map(self.__map_df)
        return self.__map_df