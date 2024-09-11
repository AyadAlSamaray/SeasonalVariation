# REU Seasonal Variation in Cosmic Ray Detection Rates

This repository contains the code used for analyzing **Seasonal Variation in Cosmic Ray Detection Rates**. This research was conducted during the REU experience, in collaboration with **Reman Adhikari** and under the mentorship of **Professor Dennis Soldin**.

## Research Summary

Our study focuses on detecting seasonal variations in cosmic ray rates using data collected from detector 1006 located in Utrecht, Netherlands. Understanding these variations helps in refining models of cosmic ray interactions with Earth's atmosphere and contributes to broader astrophysical research.

You can view our final research poster here:  
**[INSPIRE- Final research poster.pdf](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Images/INSPIRE-%20Final%20research%20poster.pdf)**

## Running the Code

To replicate our analysis:

1. Download the cosmic ray data from the HiSPARC website:  
   **[Data Source](https://data.hisparc.nl/media/jsparc/data_retrieval.html)**

2. Update the file paths in each script to point to the downloaded data. This will allow you to generate the graphs and results as demonstrated in our research.

### Scripts

- **[Average R vs Average P](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Average%20R%20vs%20Average%20P.py)** 
  _Compares the average change in Event rate against the Average change in Surface pressure_
  _![Average R vs Average P Plot](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Images/4%20Year%20Event%20Rate%20vs%20Surface%20Pressure.png)_

- **[Average Yearly Event Rate](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Average%20Yearly%20Event%20Rate.py)**  
  _Displays the relative average daily event rate divided by the total average event rate_
  _![Average Yearly Event Rate Plot](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Images/4%20Year%20Average.png)_

- **[Daily Event Rate, Surface Pressure and Relative Event Rate](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Daily%20Event%20Rate%2C%20Surface%20Pressure%20and%20Relative%20Event%20Rate.py)**  
  _Displays the Event rate, Relative event rate and Surface Pressure_ 
  _![Daily Event Rate, Surface Pressure and Relative Event Rate Plot](https://github.com/AyadAlSamaray/SeasonalVariation/blob/main/Images/Relative%20event%20rate.png)_

## Acknowledgements

This project was funded in part by the **National Science Foundation (NSF)** award # 2005973. We would like to thank Dr. Tino Nyawelo for giving us the opportunity to participate in this program. We would also like to thank REU for providing us with a workspace.
