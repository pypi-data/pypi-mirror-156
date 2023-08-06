# World Bank Data Query Tool

* Multi .csv Files 
* Transform World Bank Data Indicator
  * One Variable Panel Data
  * MultiVariable Time Series Data
  * MultiVariable Cross Section Data
  * MultiVariable Panel Data **(New!)**

## Requirements
* python 3.9.12
* pandas 1.4.2

## WorldBankDataTransform

Standard data.worldbank.org/indicator data form

![image1](assets/readme_pictures/wb_standard_data_form.PNG)

#### .onevar_panel_data(key_name, country_list, save_file=False, filename_save=None )

transformed to:

![image2](assets/readme_pictures/panel_data.PNG)

#### .multivar_time_series(country, save_file=False, filename_save=None)

transformed to:

![image 3](assets/readme_pictures/time_series_data.PNG)


#### .multivar_cross_section(year, country_list=None, save_file=False, filename_save=None)

transformed to:

![image 4](assets/readme_pictures/cross_section_data.PNG)


#### .multivar_panel_data(save_file=False, filename_save=None)

transformed to:

![image 5](assets/readme_pictures/multivar_panel_data.PNG)

# Go ahead and
## Read example.py!
