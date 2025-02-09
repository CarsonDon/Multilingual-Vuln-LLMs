import pandas as pd
import numpy as np

class Visualize():
    
    def __init__(self, model):
        self.results_path = './results/' + f'{model}_results.csv'
        self.model = model
        self.languages = ['en', 'zh-cn', 'hi', 'ko', 'th', 'bn', 'jw', 'si']
        self.act_languages = ['English', 'Chinese', 'Hindi', 'Korean', 'Thai', 'Bengali', 'Javanese', 'Sinhala']

    def calc_quant_results(self):
        Rej_bucket = []
        RS_bucket = []
        LS_bucket = [] 

        df = pd.read_csv(self.results_path)

        #calculate language wise averages
        print('\n\n-------- Language Wise Average Values ----------\n')
        for indx, language in enumerate(self.languages):
            print('Language:', self.act_languages[indx])
            Rej_bucket.append(df[f'{language}-Rej'].mean())
            print('  Rejection Score Mean - ', round(df[f'{language}-Rej'].mean(),3))
            RS_bucket.append(df[f'{language}-RS'].mean())
            print('  Relevancy Score Mean - ', round(df[f'{language}-RS'].mean(),3))
            LS_bucket.append(df[f'{language}-LS'].mean())
            print('  Legality Score Mean - ', round(df[f'{language}-LS'].mean(),3))
            print('\n')
        
        print('---------', f'Overall Performance of the {self.model} model', '--------\n')
        print('Rejection Score:', round(np.average(Rej_bucket),3))
        print('Relevancy Score:', round(np.average(RS_bucket),3))
        print('Legality Score:', round(np.average(LS_bucket),3))

        return

        #calculate language wise averages