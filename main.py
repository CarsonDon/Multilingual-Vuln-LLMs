import argparse
from process import PreProcessor
from Calc_GEval import G_Eval
from results_visualize import Visualize


def main(args, API_Key):

    model = args.model
    type = args.type

    Pre_Processor = PreProcessor(API_Key, model)
    GEval_ = G_Eval(API_Key)
    Visualizer = Visualize(model)

    if model == 'gemini':
        Pre_Processor.get_results_gemini(type)
    elif model == 'gpt_3.5':
        Pre_Processor.get_results_gpt35(type)
    elif model == 'gpt_4':
        Pre_Processor.get_results_gpt4(type)
    else:
        print('Enter a valid model name')
        return

    GEval_.calc_geval(model)
    Visualizer.calc_quant_results()
    return


    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLMs for their multilingual vulnerabilities")
    parser.add_argument("--model", type=str, default='gpt4', help="LLM model name")
    parser.add_argument("--type", type=str, default='demo', help="Size of the prompt set")

    API_Key = input("Input your relevant API key:")

    args = parser.parse_args()
    main(args, API_Key)

    