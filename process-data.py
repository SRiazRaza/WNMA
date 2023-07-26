import os
from typing import List
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import learning_curve


def dt_lookup(s):
    """
    Helper func. This is an extremely fast approach to datetime parsing.
    For large data, the same dates are often repeated. Rather than
    re-parse these, we store all unique dates, parse them, and
    use a lookup to convert all dates.

    https://stackoverflow.com/questions/29882573/pandas-slow-date-conversion
    """
    return s.map({date: pd.to_datetime(date) for date in s.unique()})


def read_drone_sweep_file_and_merge(path) -> pd.DataFrame:
    """
    Takes in the path to an output file from drone_sweep. drone_sweep spreads the output of a single sweep over
    multiple lines. This combines those lines. So that:
    - one row is one whole sweep (180 bins)
    - row indexed by datetime timestamp
    - columns (ie bins) are floor(starting_bin_freq_hz)

    With current drone_sweep settings, this yields a dataframe with 180 rows

    :param path: filepath_or_buffer : str, path object, or file-like object
    :return: pd.DataFrame
    """
    # grouped.get_group('2019-02-15 11:03:17.299693').values[:, 6:].ravel() # todo delete this line

    # Read CSV drone_sweep output to Pandas DataFrame
    drone_df: pd.DataFrame = pd.read_csv(path, header=None, low_memory=False)

    # Index everything by datetime
    datetime = pd.DatetimeIndex(dt_lookup(drone_df[0] + drone_df[1]))
    drone_df.set_index(datetime, inplace=True)

    # Group according to datetime timestamp
    # find the number of bins we are expecting, so we can discard the others. Use mode for this
    expected_num_bins = drone_df.groupby(drone_df.index).apply(lambda x: x.values[:, 6:].ravel().size).mode()
    # filter out incomplete sweeps. ie where < 180 bins
    merged_df = drone_df.groupby(drone_df.index).filter(lambda x: x.values[:, 6:].ravel().size == expected_num_bins)
    # combine multiple rows corresponding to a single sweep/timestamp into one row, datetime indexed
    merged_df = merged_df.groupby(merged_df.index).apply(lambda x: pd.Series(x.values[:, 6:].ravel()))

    num_bins = merged_df.shape[1]
    # set col name to min freq for each sample i.e. sample starting at 2400000000 hz
    min_freq = drone_df[2].min()
    max_freq = drone_df[3].max()
    bin_size = (max_freq - min_freq) / num_bins  # in hz
    merged_df.columns = [int((min_freq + x * bin_size)) for x in range(0, num_bins)]

    # FIX for scatterplot -- make sure it contains FLOATS not STRINGS!
    merged_df = merged_df.astype(float)

    return merged_df


def get_mean_by_bin(df: pd.DataFrame) -> pd.Series:
    """
    Takes all the sweep data from the input dataframe as returned by read_drone_sweep_file_and_merge
    and gets the average db for each bin.
    Returns as a pandas Series

    :param df: pd.DataFrame from experiment in question
    :return: pd.Series of average
    """
    return df.mean(axis=0)


def get_max_by_bin(df: pd.DataFrame) -> pd.Series:
    """
    Takes all the sweep data from the input dataframe as returned by read_drone_sweep_file_and_merge
    and gets the max db for each bin.
    Returns as a pandas Series

    :param df: pd.DataFrame from experiment in question
    :return: pd.Series of average
    """
    return df.max(axis=0)


def get_train_test_data(positive: List, negative: List, testSize=0.2):
    """
    Takes in string or list of string paths to data files for both positive and
    negative examples of our drone_sweep data and returns a train and test
    split of inputs and their labels


    :param positive: the list files containing positive examples
    :param negative: the list of files containing negative examples
    returns a four tuple of x_train, x_test, y_train, y_test
    """
    # 1 for positive examples (drones flying) and 0 for just random noise
    labels = [1.0, 0.0]

    labeled_data = pd.DataFrame()
    for files, label in zip([positive, negative], labels):
        for filename in files:
            new_data = read_drone_sweep_file_and_merge(filename)
            new_data['label'] = label
            labeled_data = labeled_data.append(new_data)

    labels = labeled_data['label']
    inputs = labeled_data.drop('label', axis=1)
    return train_test_split(inputs, labels, test_size=testSize)

def get_heat_map(avg_by_bin):
     # Heat Map
    # need to rename the '5 meter' file to '5' instead of '05' for this to work
    i = 5
    avgs_over_distance = avg_by_bin
    print(avgs_over_distance.shape)
    avgs_over_distance_dr = np.reshape(avgs_over_distance, (-1, 180))
    avgs_over_distance_bg = np.reshape(avgs_over_distance, (-1, 180))
    
    while i <= 50:
        filename_dr = drone_filename
        filename_bg = noise_filename
        
        parts = filename_dr.split('.')
    
        # Look for the part containing "meters"
        for part in parts:
            if 'meters' in part:
                new= part

        sample_dr = read_drone_sweep_file_and_merge(filename_dr)
        sample_bg = read_drone_sweep_file_and_merge(filename_bg)
        avg_by_bin_dr = get_mean_by_bin(sample_dr)
        avg_by_bin_bg = get_mean_by_bin(sample_bg)
        if i == 5:
            x = 0
        else:
            
            avgs_over_distance_dr = np.append(avgs_over_distance_dr, avg_by_bin_dr)
            avgs_over_distance_bg = np.append(avgs_over_distance_bg, avg_by_bin_bg)
        i = i + 5

    fig1, ax1 = plt.subplots()
    im1 = ax1.imshow(avgs_over_distance_dr)
    fig2, ax2 = plt.subplots()
    im2 = ax2.imshow(avgs_over_distance_bg)
    ax1.set_title("drone bins vs Distance to Drone")
    savefig1=current_dir+"/figures/"+new+"_heatmap_dr.png"
    plt.savefig(savefig1)
    ax2.set_title("drone bins vs Background Noise")
    savefig2=current_dir+"/figures/"+new+"_heatmap_bg.png"
    plt.savefig(savefig2)



def make_svm(x_train: pd.DataFrame, x_test: pd.DataFrame, y_train: pd.DataFrame, y_test: pd.DataFrame):
    clf = SVC(gamma='auto')
    return(clf.fit(x_train, y_train))

def plot_learning_curve(estimator: SVC, title, X, y):
    plt.figure()
    plt.title(title)
    plt.xlabel("Training Examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(estimator, X, y)
    train_scores_mean = np.mean(train_scores, axis = 1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt



def get_scatterplot(filename1, filename2):
    # Heat Map
    # need to rename the '5 meter' file to '5' instead of '05' for this to work
    sample_br = read_drone_sweep_file_and_merge(filename1)
    sample_dr = read_drone_sweep_file_and_merge(filename2)
    parts = filename1.split('.')
    
    # Look for the part containing "meters"
    for part in parts:
        if 'meters' in part:
            new= part


    max_by_bin_br = get_max_by_bin(sample_br)
    max_by_bin_dr = get_max_by_bin(sample_dr)
    #avgs_over_distance_dr = np.reshape(avgs_over_distance, (-1, 180))
    fig1, ax1 = plt.subplots()

    print(max_by_bin_dr)
    ax1.scatter(max_by_bin_br.index, max_by_bin_br.values, c="b", label="background only")
    ax1.scatter(max_by_bin_dr.index, max_by_bin_dr.values, c="r", label="drone on")

    plt.legend(loc='upper left')

    ax1.set_title("Background vs Drone Activity")
    #plt.ylim(-75, -50)
    plt.xlabel("Frequency (gHz)")
    plt.ylabel("Signal strength (dB)")
    savefig=current_dir+"/figures/"+new+"_comparison_scatter_MAX.png"
    plt.savefig(savefig)


#if __name__ == "__main__":
#    get_scatterplot('../../longdistance_withdrone.csv')


if __name__ == "__main__":
    
    current_dir=os.path.dirname(os.path.realpath(__file__))
    
    drone_filename = current_dir+"/data/2023.07.15.10_meters.csv"
    noise_filename = current_dir+"/data/2023.07.15.bg_after_10_meters.csv"

    get_scatterplot(drone_filename,noise_filename)

    # filename = "../data/25_meters.csv"
    print("Working in %s" % os.getcwd())
    print("Using file %s" % drone_filename)
    print("Example of reading in 10 meter dji data")
    print("=======================================")
    sample_data = read_drone_sweep_file_and_merge(drone_filename)
    sample_data.info()  # just print out some info about the dataframe
    print("---------------------------------------")
    print(sample_data.head(5))
    print("=======================================")
    print("\nExample of getting avg for each bin (pandas Series):")
    print("=======================================")
    avg_by_bin = get_mean_by_bin(sample_data)
    get_heat_map(avg_by_bin)
    print("Shape: %s" % avg_by_bin.shape)
    print("---------------------------------------")
    print(avg_by_bin.head(4))
    print("\t...")
    print(avg_by_bin.tail(4))
    print("=======================================")
    print("\n Creating a split of our positive and negative examples for use in learning models: ")
    x_train, x_test, y_train, y_test = get_train_test_data(positive=[drone_filename], negative=[noise_filename])
    print("Training examples: " + str(x_train.head()) + "\nTraining Labels: " + str(y_train.head()))
    
