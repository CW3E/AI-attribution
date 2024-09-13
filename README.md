# Harnessing AI data-driven global weather models for climate attribution: An analysis of the 2017 Oroville Dam extreme atmospheric river 
This repository contains the material and guidelines to reproduce the results presented in the manuscript entitled **Harnessing AI data-driven global weather models for climate attribution: An analysis of the 2017 Oroville Dam extreme atmospheric river**, submitted to *Artificial Intelligence for the Earth Systems*. The scripts provided illustrate how to perform the AI-based factual and counterfactual simulations for the atmospheric river (AR) of February 2017 which caused extreme damage in the Western United States. Scripts to generate the initial conditions for the different simulations are also provided. The NN-INIT model is shared in the `./models` folder, which is used in the initialization module to estimate some of the initial condition fields for the counterfactual simultions. The data to reproduce the results of the manuscript can be found in [1]. The repository is structured in three folders:

* sh --> jobs. The simulations were run with the European Centre for Medium-Range Weather Forecasts (ECMWF) library for AI-models, namely `ecmwf-ai`. Instructions on the installation of this library can be found at the following Github repository: https://github.com/ecmwf-lab/ai-models. 
  * `submit_graphcast-init.sh`: job to perform inference with Graphcast [2] initialized with initial conditions which have been modified with the initialization module.
  * `submit_graphcast.sh`: job to perform inference with Graphcast [2] initialized with initial conditions which have not been modified with the initialization module (only the climate change signal of the temperature variables).
  * `submit_pangu-init.sh`: job to perform inference with Pangu-Weather [3] initialized with initial conditions which have been modified with the initialization module.
  * `submit_pangu.sh`: job to perform inference with Pangu-Weather [3] initialized with initial conditions which have not been modified with the initialization module (only the climate change signal of the temperature variables).
  * `submit_sfno-init.sh`: job to perform inference with SFNO [4] initialized with initial conditions which have been modified with the initialization module.
  * `submit_sfno.sh`: job to perform inference with SFNO [4] initialized with initial conditions which have not been modified with the initialization module (only the climate change signal of the temperature variables).
* scripts --> Main executable scripts.
  * `build-initial-condition.py`: Python script that generates the initial condition for each of the simulations of the AI-models.
  * `initialization-module.py`: Python script that loads the initial condition from ERA5 for the Oroville AR simulation and modify (a) the temperature variables based on the climate change signal, (b) the Integrated water vapor, the mean sea level pressure and the surface pressure by means of the NN-INIT network, and (c) adjusts the geopotential fields based on the hydrostatic balance equation. Variables are stored and are later used in the `build-initial-condition.py` script to generate the initial conditions for each of the AI models.
  * `download_height.py`: Python script to download pressure variables from ERA5.
  * `download_surface.py`: Python script to download surface variables from ERA5.
* utils --> This folder contains the auxiliary scripts that are sourced by the main scripts during execution.


## References
[1] Baño-Medina, J., Sengupta, A., Michaelis, A., Delle Monache, L., Kalansky, J., Watson-Parris, D. (2024). Data from: Harnessing AI data-driven global weather models for climate attribution: An analysis of the 2017 Oroville Dam extreme atmospheric river. UC San Diego Library Digital Collections. Dataset. https://doi.org/10.6075/J09W0FTB

[2] Lam, R., Sanchez-Gonzalez, A., Willson, M., Wirnsberger, P., Fortunato, M., Alet, F., ... & Battaglia, P. (2023). Learning skillful medium-range global weather forecasting. Science, 382(6677), 1416-1421.

[3] Bi, K., Xie, L., Zhang, H., Chen, X., Gu, X., & Tian, Q. (2023). Accurate medium-range global weather forecasting with 3D neural networks. Nature, 619(7970), 533-538.

[4] Bonev, B., Kurth, T., Hundt, C., Pathak, J., Baust, M., Kashinath, K., & Anandkumar, A. (2023, July). Spherical fourier neural operators: Learning stable dynamics on the sphere. In International conference on machine learning (pp. 2806-2823). PMLR.
