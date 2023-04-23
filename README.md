![Portada](https://github.com/Dancar96/Antiphishing-Model/blob/main/img/Portada.PNG)

# <h1 align="center"> 🎣 Antiphishing Model 🎣

An ML project for unmask non-legitimate URL's.

This first project has been realized using Python and the libraries: ![NumPy](https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white)  ![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)  ![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

For the choice of the ML model, a comparison of supervised language models was made according to their Recall evaluation metric. It has been decided to use this metric since it is the most optimal for our data, given that if we are going to classify URL's as legitimate or phishing, we must prioritize that no phishing URL is classified as legitimate, it is preferable that if the prediction is wrong it is because it classifies a legitimate URL as phishing than the other way around.

After the comparison of models according to their recall score, the model chosen is 'XGBClassifier' with the optimal hyperparameters for the dataset according to the 'GridSearchCV' performed.

The model is learned and then saved as a pickle file.

![Corr_Matrix](https://github.com/Dancar96/Antiphishing-Model/blob/main/img/EDA%20Phishing%203.PNG)

![Confusion_matrix](https://github.com/Dancar96/Antiphishing-Model/blob/main/img/Matriz%20confusi%C3%B3n.PNG)
