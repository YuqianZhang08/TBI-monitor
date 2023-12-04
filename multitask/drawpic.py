import pandas as pd
from matplotlib import pyplot as plt

from preprocess import noise_reduction


def get_data_from_excel(excelpath, sheetname):
     
    data = pd.read_excel(excelpath, sheet_name=sheetname, header=0)
    names = [name for name in data]
    data_all = []
    label_all = []
    bochang = [value[0] for value in data.values]
    for i in range(len(names)-1):
        values = [value[i+1] for value in data.values]
        label_all.append(names[i+1])
        data_all.append(values)
    return data_all, label_all, bochang


def draw_temperature_spectrals(data_all, bochang):
    plt.title('Temperature Spectrum', fontsize='20', font='Arial')
    plt.plot(bochang, data_all[0], marker=",", lw=1, label="34 ℃")
    plt.plot(bochang, data_all[1], marker=",", lw=1, label="34.5 ℃")
    plt.plot(bochang, data_all[2], marker=",", lw=1, label="35 ℃")
    plt.plot(bochang, data_all[3], marker=",", lw=1, label="35.5 ℃")
    plt.plot(bochang, data_all[4], marker=",", lw=1, label="36 ℃")
    plt.plot(bochang, data_all[5], marker=",", lw=1, label="36.5 ℃")
    plt.plot(bochang, data_all[6], marker=",", lw=1, label="37 ℃")
    plt.plot(bochang, data_all[7], marker=",", lw=1, label="37.5 ℃")
    plt.plot(bochang, data_all[8], marker=",", lw=1, label="38 ℃")
    plt.plot(bochang, data_all[9], marker=",", lw=1, label="38.5 ℃")
    plt.plot(bochang, data_all[10], marker=",", lw=1, label="39 ℃")
    plt.plot(bochang, data_all[11], marker=",", lw=1, label="39.5 ℃")
    plt.plot(bochang, data_all[12], marker=",", lw=1, label="40 ℃")
    plt.plot(bochang, data_all[13], marker=",", lw=1, label="41 ℃")
    plt.plot(bochang, data_all[14], marker=",", lw=1, label="42 ℃")
    #plt.xlim(450,600)
    plt.xlabel("Wavelength", font='Arial', fontsize='20')
    plt.ylabel("Spectral Value", font='Arial', fontsize='20')
    plt.tick_params(labelsize=20)
    plt.legend(fontsize='large')
    plt.show()


def draw_GLU_spectrals(data_all, bochang):
    plt.title('Glucose Concentration Spectrum', fontsize='20', font='Arial')
    plt.plot(bochang, data_all[0], marker=",", lw=1, label="0 mmol/L")
    plt.plot(bochang, data_all[1], marker=",", lw=1, label="1 mmol/L")
    plt.plot(bochang, data_all[2], marker=",", lw=1, label="2 mmol/L")
    plt.plot(bochang, data_all[3], marker=",", lw=1, label="3 mmol/L")
    plt.plot(bochang, data_all[4], marker=",", lw=1, label="4 mmol/L")
    plt.plot(bochang, data_all[5], marker=",", lw=1, label="5 mmol/L")
    plt.plot(bochang, data_all[6], marker=",", lw=1, label="6 mmol/L")
    #plt.xlim(550,700)
    plt.xlabel("Wavelength", font='Arial', fontsize='20')
    plt.ylabel("Spectral Value", font='Arial', fontsize='20')
    plt.tick_params(labelsize=20)
    plt.legend(fontsize='large')
    plt.show()

def draw_PH_spectrals(data_all, bochang):
    plt.title('PH Spectrum', fontsize='20', font='Arial')
    plt.plot(bochang, data_all[0], marker=",", lw=1, label="PH = 6")
    plt.plot(bochang, data_all[1], marker=",", lw=1, label="PH = 6.4")
    plt.plot(bochang, data_all[2], marker=",", lw=1, label="PH = 6.8")
    plt.plot(bochang, data_all[3], marker=",", lw=1, label="PH = 7.2")
    plt.plot(bochang, data_all[4], marker=",", lw=1, label="PH = 7.6")
    plt.plot(bochang, data_all[5], marker=",", lw=1, label="PH = 8")
    #plt.xlim(500,700)
    plt.xlabel("Wavelength", font='Arial', fontsize='20')
    plt.ylabel("Normalized Reflection Intensity(I/I0)", font='Arial', fontsize='20')
    plt.tick_params(labelsize=20)
    plt.legend(fontsize='large')
    plt.show()

def draw_noise_reduct():
    excelpath = "datasets.xlsx"
    sheetname = 'temperature'
    temper_data, _, bochang = get_data_from_excel(excelpath, sheetname)
    temper_or = temper_data.copy()
    temper_data_no = noise_reduction(temper_data)
    print(temper_or[0])
    print(temper_data_no[0])

    fig1 = plt.subplot(2, 2, 1)
    plt.title('Before Noise Reduction', fontsize='20', font='Arial')
    fig1.scatter(bochang, temper_or[0], marker=".", lw=1, c='b')
    plt.ylim(0, 40)
    plt.tick_params(labelsize=15)
    plt.xlabel("Wavelength", font='Arial', fontsize='16')
    plt.ylabel("Spectral Value Temperature = 34 ℃", font='Arial', fontsize='16')
    fig2 = plt.subplot(2, 2, 2)
    plt.title('After Noise Reduction', fontsize='20', font='Arial')
    fig2.scatter(bochang, temper_data_no[0], marker=".", lw=1, c='g')
    plt.ylim(0, 40)
    plt.tick_params(labelsize=15)
    plt.xlabel("Wavelength", font='Arial', fontsize='16')
    plt.ylabel("Spectral Value Temperature = 34 ℃", font='Arial', fontsize='16')

    fig3 = plt.subplot(2, 2, 3)
    fig3.scatter(bochang, temper_or[7], marker=".", lw=1, c='b')
    plt.ylim(0, 40)
    plt.tick_params(labelsize=15)
    plt.xlabel("Wavelength", font='Arial', fontsize='16')
    plt.ylabel("Spectral Value Temperature = 37.5 ℃", font='Arial', fontsize='16')
    fig4 = plt.subplot(2, 2, 4)
    fig4.scatter(bochang, temper_data_no[7], marker=".", lw=1, c='g')
    plt.ylim(0, 40)
    plt.tick_params(labelsize=15)
    plt.xlabel("Wavelength", font='Arial', fontsize='16')
    plt.ylabel("Spectral Value Temperature = 37.5 ℃", font='Arial', fontsize='16')
    plt.show()


if __name__ == '__main__':
     #excepath = r"C:\Users\86151\Desktop\neural network code\glu.xlsx"
     #sheetname = r"ori"
     #data_all, _, bochang = get_data_from_excel(excepath, sheetname)
     #draw_temperature_spectrals(data_all, bochang)
#
     excepath = r"C:\Users\86151\Desktop\neural network code\ph.xlsx"
     sheetname = r"Sheet1"
     data_all, _, bochang = get_data_from_excel(excepath, sheetname)
     draw_GLU_spectrals(data_all, bochang)
#
    #excepath = r"C:\Users\86151\Desktop\neural network code\temp.xlsx"
    #sheetname = r"Sheet2"
    #data_all, _, bochang = get_data_from_excel(excepath, sheetname)
    #draw_PH_spectrals(data_all, bochang)

     #draw_noise_reduct()