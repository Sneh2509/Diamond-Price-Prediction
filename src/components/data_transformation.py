import os
import sys

from dataclasses import dataclass

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from src.logger import logging
from src.exception import CustomException
from src.utils import save_object



# Intitialize the Data Transformation Configuration
@dataclass
class DataTransformationconfig:
    preprocessor_obj_file_path = os.path.join('artifacts', 'preprocessor.pkl')


# create a class for Data Transformation
class DataTransformation:
    def __init__(self) -> None:
        self.data_transformation_config = DataTransformationconfig()

    def get_data_transformation_object(self):
        try:
            logging.info('Data Transformation initiated')

            # Define which columns should be ordinal-encoded and which should be scaled
            categorical_cols = ['cut', 'color','clarity']
            numerical_cols = ['carat', 'depth','table', 'x', 'y', 'z']
            
            # Define the custom ranking for each ordinal variable
            cut_categories = ['Fair', 'Good', 'Very Good','Premium','Ideal']
            color_categories = ['D', 'E', 'F', 'G', 'H', 'I', 'J']
            clarity_categories = ['I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF']

            logging.info('Pipeline Initiated')
            # Create the preprocessor pipeline
            # Numerical Pipeline
            numerical_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ])

            # Categorical Pipeline
            categorical_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('ordinal', OrdinalEncoder(categories=[cut_categories,color_categories,clarity_categories])),
                ('scaler', StandardScaler())
            ])

            # Preprocessing
            preprocessor = ColumnTransformer([
                ('num_pipeline', numerical_pipeline, numerical_cols),
                ('cat_pipeline', categorical_pipeline, categorical_cols)
            ])

            logging.info('Pipeline Completed')
            
            return preprocessor

        except Exception as e:
            logging.info('Exception occured at Data Transformation stage')
            raise CustomException(e,sys)
        

    def initiate_data_transformation(self, train_path, test_path):
        try:
            # Reading train and test data
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info('Read train and test data completed')
            logging.info(f'Train Dataframe Head : \n{train_df.head().to_string()}')
            logging.info(f'Test Dataframe Head  : \n{test_df.head().to_string()}')

            logging.info('Obtaining preprocessing object')
            preprocessing_obj = self.get_data_transformation_object()

            target_column_name = 'price'
            drop_column = [target_column_name, 'id']

            input_feature_train_df = train_df.drop(columns=drop_column, axis=1)
            input_feature_test_df = test_df.drop(columns=drop_column, axis=1)

            target_feature_train_df = train_df[target_column_name]
            target_feature_test_df = test_df[target_column_name]

            ## Trnasformating using preprocessor obj
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            logging.info("Applying preprocessing object on training and testing datasets.")
            

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )
            logging.info('Preprocessor pickle file saved')

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            logging.info('Exception occured at Data Transformation stage')
            raise CustomException(e,sys)