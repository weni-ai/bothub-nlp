import math
import matplotlib.pyplot as plt
import numpy as np

from bothub_nlp_rasa_utils.utils import backend


def score_normal(x,  optimal):
    """
        Based on normal distribution,
        score will decay if current value is below or above target
    """
    slim_const = 2
    result = math.exp(-((x - optimal) ** 2) / (2 * (optimal/slim_const) ** 2))
    return result * 100


def score_cumulated(x, optimal):
    """
        Based on cumulated distribution,
        score will increase as close current value is to the target
    """
    factor = 10/optimal
    sigma_func = 1/(1 + np.exp(-(-5 + x*factor)))
    return sigma_func * 100


def plot_func(func, optimal):

    x = np.linspace(0, 2*optimal, 100)
    y = [func(n, optimal=optimal) for n in x]

    plt.plot(x, y)
    plt.plot([optimal, optimal], [0, 100])
    plt.ylabel('score')
    plt.xlabel('distance')
    plt.show()


def intentions_balance_score(dataset):
    intentions = dataset["intentions"]
    sentences = dataset["train"]

    intentions_count = len(intentions)
    if intentions_count < 2:
        return 0

    train_count = dataset["train_count"]

    scores = []
    for intention in sentences.keys():
        this_size = len(sentences[intention])
        excl_size = train_count - this_size

        # Mean of sentences/intention excluding this intention
        # It is the optimal target
        excl_mean = excl_size/(intentions_count-1)
        # print(this_size, excl_mean)
        scores.append(score_normal(this_size, excl_mean))

    score = sum(scores)/len(scores)

    return {
        "score": score,
        "recommended": f"The avarage sentences per intention is {int(train_count/intentions_count)}"
    }


def intentions_size_score(dataset):
    intentions = dataset["intentions"]
    sentences = dataset["train"]

    intentions_count = len(intentions)
    if intentions_count < 2:
        return 0

    optimal = int(106.6556 + (19.75708 - 106.6556)/(1 + (intentions_count/8.791823)**1.898546))

    scores = []
    for intention in sentences.keys():
        this_size = len(sentences[intention])
        if this_size >= optimal:
            scores.append(1.0)
        else:
            scores.append(score_cumulated(this_size, optimal))

    score = sum(scores)/len(scores)

    return {
        "score": score,
        "recommended": f"{optimal} sentences per intention"
    }


def evaluate_size_score(dataset):
    intentions = dataset["intentions"]

    intentions_size = len(intentions)
    if intentions_size < 2:
        return 0

    train_count = dataset["train_count"]
    evaluate_count = dataset["evaluate_count"]

    optimal = int(692.4702 + (-1.396326 - 692.4702) / (1 + (train_count / 5646.078) ** 0.7374176))

    if evaluate_count >= optimal:
        score = 1.0
    else:
        score = score_cumulated(evaluate_count, optimal)

    return {
        "score": score,
        "recommended": f"{optimal} evaluation sentences"
    }


# TODO: word distribution score

def arrange_data(train_data, eval_data):
    dataset = {
        "intentions": [],
        "train_count": len(train_data),
        "train": {},
        "evaluate_count": len(eval_data),
        "evaluate": {}
    }

    for data in train_data:
        if data["intent"] not in dataset["intentions"]:
            dataset["intentions"].append(data["intent"])
            dataset["train"][data["intent"]] = []

        dataset["train"][data["intent"]].append(data["text"])

    for data in eval_data:
        if data["intent"] not in dataset["intentions"]:
            continue
        if data["intent"] not in dataset["evaluate"]:
            dataset["evaluate"][data["intent"]] = []

        dataset["evaluate"][data["intent"]].append(data["text"])

    return dataset


def get_scores(repository_version, repository_authorization):

    train_data = backend().request_backend_get_examples(
        repository_version, False, None, repository_authorization
    ).get("results")
    # print(train_data)

    eval_data = backend().request_backend_start_evaluation(
        repository_version,
        repository_authorization
    )
    # print(eval_data)

    dataset = arrange_data(train_data, eval_data)

    scores = {
        "intentions_balance": intentions_balance_score(dataset),
        "intentions_size": intentions_size_score(dataset),
        "evaluate_size": evaluate_size_score(dataset)
    }

    sum = 0
    for n in scores.keys():
        sum += scores[n]["score"]
    average = sum/len(scores)

    scores["average"] = average

    return scores


if __name__ == "__main__":
    mocked_repository_example = {
        "intentions": ["a", "b", "c", "d", "e"],
        "train_count": 103,
        "train": {
            "a": ["intenção A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A",
                  "outra frase da A", "outra frase da A"],
            "b": ["intenção B", "outra frase da B", "frase 3", "frase 4", "frase 5"],
            "c": ["intenção C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C",
                  "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C",
                  "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C",
                  "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C",
                  "outra frase da C", "outra frase da C", "outra frase da C"],
            "d": ["intenção D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D",
                  "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D",
                  "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D"],
            "e": ["intenção E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E",
                  "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E",
                  "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E",
                  "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E"],
        },
        "evaluate_count": 29,
        "evaluate": {
            "a": ["teste A", "outra frase teste da A", "outra frase teste da A", "outra frase teste da A",
                  "outra frase teste da A"],
            "b": ["teste B", "outra frase teste da B", "frase teste3", "frase teste4", "frase teste5"],
            "c": ["teste C", "outra frase teste da C", "outra frase teste da C", "outra frase teste da C",
                  "outra frase teste da C"],
            "d": ["teste D", "outra frase teste da D", "outra frase teste da D", "outra frase teste da D",
                  "outra frase teste da D", "outra frase teste da D", "outra frase teste da D"],
            "e": ["teste E", "outra frase teste da E", "outra frase teste da E", "outra frase teste da E",
                  "outra frase teste da E", "outra frase teste da E", "outra frase teste da E"],
        }
    }

    plot_func(score_cumulated, 50)
    plot_func(score_normal, 50)

    sc = intentions_balance_score(
        mocked_repository_example
    )

    print(sc["score"], sc["recommended"])
