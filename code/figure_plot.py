from embedding_eval import spearman_correlation
import matplotlib.pyplot as plt
import matplotlib.lines as lines
plt.rcParams['font.sans-serif'] = ['SimHei']
from utils import *
plt.rcParams['axes.unicode_minus'] = False
def get_fd():
    fd_path =ROOT.parent /'Diachronic_sub-database'/ 'time_series' / 'Diachronic_character_frequency_diversities.csv'
    data=pd.read_csv(fd_path)

    fd_dict={}
    columns=[f'{dy}_log_fd' for dy in 'Song Yuan Ming Qing'.split()]
    for index,row in data.iterrows():
        word=row['Character']
        values=[row[col] for col in columns]
        fd_dict[word]=values
    return fd_dict



def get_entropy():

    entropy_path = ROOT.parent / 'Diachronic_sub-database'/'time_series'/ 'Diachronic_entropies.csv'
    data=pd.read_csv(entropy_path)
    left_dict={}
    right_dict={}

    left_columns=[f'{dy}_left_entropy' for dy in 'Tang Song Yuan Ming Qing'.split()]
    right_columns = [f'{dy}_right_entropy' for dy in 'Tang Song Yuan Ming Qing'.split()]
    for index,row in data.iterrows():
        word=row['Character']
        left_values=[row[col] for col in left_columns]
        right_values = [row[col] for col in right_columns]
        left_dict[word]=left_values
        right_dict[word]=right_values
    return left_dict,right_dict

def ind_legend(words,pinyin,colors):
    handles=[]
    for i,w in enumerate(words):
        label=w+'('+pinyin[i]+')'
        line=lines.Line2D([0], [0], label=label,color=colors[i],linestyle='solid')
        handles.append(line)

    return handles
def plot_freq(ax, words,pinyin):
    x = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']
    colors = ['r', 'g', 'y', 'b']
    linestyle = 'solid'
    fd_dict=get_fd()
    for i, word in enumerate(words):
        fd=[0]+fd_dict.get(word)
        ax.plot(x, fd, label=pinyin[i], color=colors[i], linestyle=linestyle)

    ax.set_xlim(0.0, len(x)-1)
    ax.grid()
    ax.set_ylabel('Frequency Diversity')
    handles = ind_legend(words, pinyin, colors)
    ax.legend(handles=handles, borderpad=0.1, loc='best', fontsize=15)

def plot_entropy(ax, words,pinyin):
    colors = ['r', 'g', 'y', 'b']

    x = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']

    linestyles = ['solid', 'dashed']
    left_dict, right_dict = get_entropy()
    for i, word in enumerate(words):
        left_label = f"{word}_left"
        right_label = f"{word}_right"
        ax.plot(x, left_dict.get(word, [0] * len(x)), label=left_label, color=colors[i], linestyle=linestyles[0])
        ax.plot(x, right_dict.get(word, [0] * len(x)), label=right_label, color=colors[i], linestyle=linestyles[1])

    ax.set_xlim(0.0, len(x)-1)
    ax.grid()
    ax.set_ylabel('Entropy',fontsize=12)


def plot_similarity(ax, words,pinyin):
    ts, _, _, _ = spearman_correlation('Tang', 'Song')
    ty, _, _, _ = spearman_correlation('Tang', 'Yuan')
    tm, _, _, _ = spearman_correlation('Tang', 'Ming')
    tq, _, _, _ = spearman_correlation('Tang', 'Qing')

    colors = ['r', 'g', 'y', 'b']

    x = ['Song', 'Yuan', 'Ming', 'Qing']

    for i, word in enumerate(words):
        sim_list = [ts.get(word, 0),ty.get(word, 0),tm.get(word, 0),tq.get(word, 0)]
        print(word)
        print(sim_list)
        ax.plot(x, sim_list, label=pinyin[i], color=colors[i], linestyle='solid')

    ax.set_xlim(0.0, len(x)-1)
    # ax.set_ylim(0,0.7)
    ax.grid()
    ax.set_ylabel('Similarity')
    # handles = ind_legend(words,pinyin,colors)
    # ax.legend(handles=handles,borderpad=0.1, loc='best',fontsize=15)

def plot_combined(words,pinyin):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Frequency Diversity Plot
    plot_freq(axs[0], words,pinyin)
    axs[0].text(0.5, -0.2, 'a.', transform=axs[0].transAxes, fontsize=14, fontweight='bold',ha='right',va='bottom')
    # Entropy Plot
    plot_entropy(axs[1], words,pinyin)
    axs[1].text(0.5, -0.2, 'b.', transform=axs[1].transAxes, fontsize=14, fontweight='bold', ha='right', va='bottom')
    # Similarity Plot
    plot_similarity(axs[2], words,pinyin)
    axs[2].text(0.5, -0.2, 'c.', transform=axs[2].transAxes, fontsize=14, fontweight='bold', ha='right', va='bottom')

    plt.tight_layout()
    handles = []
    for ax in axs:
        handles.extend(ax.get_legend_handles_labels()[0])
    labels = [handle.get_label() for handle in handles]
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.2, 0.5))

    plt.tight_layout()
    save_path=OUTPUT / 'combined_plot.png'
    plt.savefig(save_path)
    plt.show()

if __name__ == "__main__":
    tests='山 舟 终 比'.split()
    pinyin=[get_pinyin(word) for word in tests]
    plot_combined(tests,pinyin)