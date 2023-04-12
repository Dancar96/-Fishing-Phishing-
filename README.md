# <h1 align="center"> 🎣 Fishing Phishing 🎣

An online tool project for unmask non-legitimate URL's.

This first project has been realized using Python and the libraries: NumPy, Pandas, MatplotLib, RegEx and Scikit-Learn.  

For the choice of the ML model, a comparison of supervised language models was made according to their Recall evaluation metric. It has been decided to use this metric since it is the most optimal for our data, given that if we are going to classify URL's as legitimate or phishing, we must prioritize that no phishing URL is classified as legitimate, it is preferable that if the prediction is wrong it is because it classifies a legitimate URL as phishing than the other way around.

