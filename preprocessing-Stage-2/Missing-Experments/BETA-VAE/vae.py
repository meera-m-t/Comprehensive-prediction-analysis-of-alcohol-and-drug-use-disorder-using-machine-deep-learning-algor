import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from autoencodersbetaVAE import VariationalAutoencoder
import pandas as pd
import random
import tensorflow as tf
import sys
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='config.json', help='configuration json file')

if __name__ == '__main__':
    
        args = parser.parse_args()
        with open(args.config) as f:
            config = json.load(f)
    
        training_epochs=config["training_epochs"] #250
        batch_size=config["batch_size"] #250
        learning_rate=config["learning_rate"] #0.0005
        latent_size = config["latent_size"] #200    
        hidden_size_1=config["hidden_size_1"]
        hidden_size_2=config["hidden_size_2"]
        beta=config["beta"]            
        data_path =   config["data_path"]     
        corrupt_data_path = config["corrupt_data_path"]
        save_root = config["save_rootpath"]
        

        data = pd.read_csv(data_path).values
        data_missing = pd.read_csv(corrupt_data_path).values

        n_row = data_missing.shape[1] # dimensionality of data space
        non_missing_row_ind= np.where(np.isfinite(np.sum(data_missing,axis=1)))
        na_ind = np.where(np.isnan(data_missing))

        sc = StandardScaler()
        data_missing_complete = np.copy(data_missing[non_missing_row_ind[0],:])
        sc.fit(data_missing_complete)
        data_missing[na_ind] = 0
        data_missing = sc.transform(data_missing)
        data_missing[na_ind] = np.nan
        del data_missing_complete
        data = sc.transform(data)

       
        # VAE network size:
        Decoder_hidden1 = hidden_size_1 #6000
        Decoder_hidden2 = hidden_size_2 #2000
        Encoder_hidden1 = hidden_size_2 #2000
        Encoder_hidden2 = hidden_size_1 #6000
                
                
        # define dict for network structure:
        network_architecture = \
            dict(n_hidden_recog_1=Encoder_hidden1, # 1st layer encoder neurons
                 n_hidden_recog_2=Encoder_hidden2, # 2nd layer encoder neurons
                 n_hidden_gener_1=Decoder_hidden1, # 1st layer decoder neurons
                 n_hidden_gener_2=Decoder_hidden2, # 2nd layer decoder neurons
                 n_input=n_row, # data input size
                 n_z=latent_size)  # dimensionality of latent space
        
        # initialise VAE:
        vae = VariationalAutoencoder(network_architecture,
                                     learning_rate=learning_rate, 
                                     batch_size=batch_size,istrain=True,restore_path=None,
                                     beta=beta)
        
        # train VAE on corrupted data:
        vae = vae.train(data=data_missing,
                        training_epochs=training_epochs)
                
        saver = tf.train.Saver()
        save_path = saver.save(vae.sess, save_root+"ep"+str(training_epochs)+"_bs"+str(batch_size)+"_lr"+str(learning_rate)+"_bn"+str(latent_size)+"_opADAM"+"_beta"+str(beta)+"_betaVAE"+".ckpt")
        
        
        
        
        