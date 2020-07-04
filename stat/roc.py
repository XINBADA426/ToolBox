#!/Bio/User/renchaobo/software/miniconda3/bin/python
# -*- coding: utf-8 -*-
# @Author: Ming
# @Date:   2020-07-03 08:02:00
# @Last Modified by:   Ming
# @Last Modified time: 2020-07-04 23:02:03
import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import roc_curve, auc
import numpy as np
import pandas as pd
import logging
import click
import os

#### Some Functions ####
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
__version__ = '1.0.0'


def plot_roc(dict_fpr, dict_tpr, dict_auc, prefix):
    """
    Plot the ROC curve
    """
    plt.figure()
    figure, ax = plt.subplots(figsize=(8, 8))
    lw = 1
    ax.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    for key, value in dict_fpr.items():
        ax.plot(dict_fpr[key], dict_tpr[key], color='darkorange', lw=lw,
                label='ROC curve of %s (AUC = %0.2f)' % (key, dict_auc[key]))
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    ax.set_xlabel('False Positive Rate', fontsize=15)
    ax.set_ylabel('True Positive Rate', fontsize=15)
    ax.set_title('ROC', fontsize=22)
    plt.legend(loc="lower right")
    plt.savefig(prefix + '.svg', bbox_inches='tight')
    plt.savefig(prefix + '.png', dpi=300, bbox_inches='tight')


########################


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """
    Tools for ROC analysis
    """
    pass


@click.command()
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option('--split/--no-split',
              default=False,
              show_default=True,
              help="Whether split the plot by featrues")
@click.option('--control',
              default='0',
              show_default=True,
              type=str,
              help="The control label")
@click.option('--treatment',
              default='1',
              show_default=True,
              type=str,
              help="The treatment label")
@click.option('-o', "--out",
              default="./",
              show_default=True,
              help="The out put dir")
def analysis(input, split, control, treatment, out):
    """
    Do ROC analysis and plot ROC curve
    """
    df = pd.read_csv(input, sep='\t')
    classify_name = df.columns[0]
    features = df.columns[1:]
    classify_type = set(df[classify_name])
    if len(classify_type) == 1:
        logging.error(
            f"File {input} column {classify_name} only have one kind label")
    elif len(classify_type) > 2:
        logging.error(
            f"File {input} column {classify_name} have more than two label")
    else:
        y = [i[0] for i in label_binarize(
            df[classify_name], classes=[control, treatment])]

        fpr = {}
        tpr = {}
        threshold = {}
        roc_auc = {}

        logging.info('ROC analysis...')
        for feature in features:
            x = df[feature]
            fpr[feature], tpr[feature], threshold[feature] = roc_curve(y, x)
            roc_auc[feature] = auc(fpr[feature], tpr[feature])

    logging.info('Plot the ROC curve...')
    if split:
        for feature in features:
            prefix = os.path.join(out, f"ROC.{feature}")
            plot_roc({feature: fpr[feature]}, {feature: tpr[feature]}, {
                feature: roc_auc[feature]}, prefix)
    else:
        prefix = os.path.join(out, "ROC")
        plot_roc(fpr, tpr, roc_auc, prefix)


@click.command()
@click.option('-i', '--input',
              required=True,
              type=click.Path(),
              help="The input table file")
@click.option("--classifier",
              default="LogisticRegression",
              show_default=True,
              type=click.Choice(
                  ["LogisticRegression", "SGDClassifier", "SVM"]),
              help="The classifier to use")
@click.option('--method',
              default="micro",
              show_default=True,
              type=click.Choice(['micro', 'macro']),
              help="Whether method to do multi ROC")
@click.option('--test_size',
              default=0.5,
              show_default=True,
              type=float,
              help="The test size percent")
@click.option('-o', "--out",
              default="./",
              show_default=True,
              help="The out put dir")
def multi(input, classifier, method, test_size, out):
    """
    Do multi class ROC analysis
    """
    df = pd.read_csv(input, sep='\t')
    classify_name = df.columns[0]
    classify_type = df[classify_name].astype("category").dtype.categories
    if len(classify_type) == 1:
        logging.error(
            f"File {input} column {classify_name} only have one kind label")
    else:
        x = df.iloc[:, 1:]
        y = label_binarize(df[classify_name], classes=classify_type)
        n_classes = y.shape[1]
        logging.info(f"Train the model with {classifier}...")
        x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                            test_size=test_size,
                                                            random_state=0)

        random_state = np.random.RandomState(0)

        if classifier == "LogisticRegression":
            from sklearn.linear_model import LogisticRegression
            classifier_method = LogisticRegression()
        elif classifier == "SGDClassifier":
            from sklearn.linear_model import SGDClassifier
            classifier_method = SGDClassifier()
        elif classifier == "SVM":
            from sklearn import svm
            classifier_method = svm.SVC(kernel='rbf',
                                        random_state=random_state)

        model = OneVsRestClassifier(classifier_method)
        y_score = model.fit(x_train, y_train).decision_function(x_test)

        logging.info(f"ROC analysis with {method}...")
        if method == "micro":
            fpr, tpr, _ = roc_curve(
                np.array(y_test).ravel(), np.array(y_score).ravel())
            roc_auc = auc(fpr, tpr)
            prefix = os.path.join(out, "ROC.micro")
            plot_roc({"micro": fpr}, {"micro": tpr},
                     {"micro": roc_auc}, prefix)

        elif method == "macro":
            fpr = dict()
            tpr = dict()
            roc_auc = dict()
            for i in range(n_classes):
                fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])

            all_fpr = np.unique(np.concatenate(
                [fpr[i] for i in range(n_classes)]))
            mean_tpr = np.zeros_like(all_fpr)

            for i in range(n_classes):
                mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])

            mean_tpr /= n_classes
            fpr = all_fpr
            tpr = mean_tpr
            roc_auc = auc(fpr, tpr)

        logging.info('Plot the ROC curve...')
        prefix = os.path.join(out, f"ROC.{method}")
        plot_roc({method: fpr}, {method: tpr}, {method: roc_auc}, prefix)


cli.add_command(analysis)
cli.add_command(multi)

if __name__ == "__main__":
    cli()
