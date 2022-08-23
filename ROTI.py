import os
import numpy as np
import datetime

class RotiCalculator(object):

    def calculate(self, atec_dict, measures_tday, tec_input):
      
        roti_dict = []      
        for prn, atec in atec_dict.items():   

            dict = Measures()
            dict.prn = prn
            dict.rot = []
            dict.roti = np.array([])
            dict.rot_time = []
            dict.roti_time = np.array([])
                   
            try: 
                stec = atec
                time = next(filter(lambda x: x.prn == prn, measures_tday)).time
                decimal_time = [(i.hour + i.minute/60. +i. second/(3600.)) for i in time]

                vls, cnts, id_dict, mode, delta_hora =  timeGap.calculate(time, None)   

                try:
                    if mode[0] == 1: 
                        step_hora = 60
                    elif mode[0] == 15:
                        step_hora = 4
                    elif mode[0] == 30:
                        step_hora = 2
                except:
                    print("ROTI: Error in the step_hora")

                rot = []
                roti = []
                rot_tstamps = []
                roti_tstamps = []
                for i in range(len(vls)): 

                    delta_time = decimal_time[id_dict[i][-1]]-decimal_time[id_dict[i][0]]     

                    deltahora = [delta_hora[k] for k in id_dict[i]]    
                    t_temp = [time[k] for k in id_dict[i]]                     
                    stec_temp = [stec[k] for k in id_dict[i]]

                    shift_stec = np.roll(stec_temp, -1)
                    rot_0 = (shift_stec - stec_temp)
                    rot_1 = (rot_0[1:len(rot_0)-1]/(deltahora[1:len(rot_0)-1]))*60.
                    rot.extend(rot_1)
                    rot_tstamps.extend(t_temp[1:len(t_temp)-1])

                    if float(delta_time) >= 0.166667:                

                        for j in range(step_hora, len(rot_1)-step_hora, step_hora):
                            rot_2 = np.sqrt(np.mean(np.power(rot_1[j-step_hora:j+step_hora], 2)) - np.power(np.mean(rot_1[j-step_hora:j+step_hora]), 2))
                            roti.append(rot_2)
                            roti_tstamps.append(t_temp[j])
                        
                dict = Measures()
                dict.prn = prn
                dict.rot = rot
                dict.roti = np.array(roti)
                dict.rot_time = rot_tstamps
                dict.roti_time = np.array(roti_tstamps)
                roti_dict.append(dict)

                del rot, roti, rot_tstamps, roti_tstamps
            
            except:
                roti_dict.append(dict)
                e = f'[ERROR] [{os.path.basename(tec_input.rinex_filepath)}] [{os.path.basename(__file__)}] Exception in ROTI calculus on {prn}'
                file_date = datetime.strptime(f'{tec_input.year} {tec_input.doy}', '%Y %j')
                logwhiter = LogFileWriter(tec_input.output_folder_path, file_date, e)
                logwhiter.whiter()
        
        return roti_dict

       
