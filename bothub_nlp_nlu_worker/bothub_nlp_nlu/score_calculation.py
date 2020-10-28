import math
import matplotlib.pyplot as plt
import numpy as np

from bothub_nlp_rasa_utils.utils import backend


def score_normal(x, optimal):
    """
        Based on normal distribution,
        score will decay if current value is below or above target
    """

    try:
        slim_const = 2
        result = math.exp(-((x - optimal) ** 2) / (2 * (optimal / slim_const) ** 2))
    except ZeroDivisionError:
        return 100

    return result * 100


def score_cumulated(x, optimal):
    """
        Based on cumulated distribution,
        score will increase as close current value is to the target
    """

    try:
        factor = 10 / optimal
        sigma_func = 1 / (1 + np.exp(-(-5 + x * factor)))
    except ZeroDivisionError:
        return 100

    return sigma_func * 100


def intentions_balance_score(dataset):
    intentions = dataset["intentions"]
    sentences = dataset["train"]

    intentions_count = len(intentions)
    if intentions_count < 2:
        return 0

    train_count = dataset["train_count"]

    scores = []
    for intention in sentences.keys():
        this_size = sentences[intention]
        excl_size = train_count - this_size

        # Mean of sentences/intention excluding this intention
        # It is the optimal target
        excl_mean = excl_size / (intentions_count - 1)
        # print(this_size, excl_mean)
        scores.append(score_normal(this_size, excl_mean))

    score = sum(scores) / len(scores)

    return {
        "score": score,
        "recommended": f"The avarage sentences per intention is {int(train_count/intentions_count)}",
    }


def intentions_size_score(dataset):
    intentions = dataset["intentions"]
    sentences = dataset["train"]

    intentions_count = len(intentions)
    if intentions_count < 2:
        return 0

    optimal = int(
        106.6556
        + (19.75708 - 106.6556) / (1 + (intentions_count / 8.791823) ** 1.898546)
    )

    scores = []
    for intention in sentences.keys():
        this_size = sentences[intention]
        if this_size >= optimal:
            scores.append(1.0)
        else:
            scores.append(score_cumulated(this_size, optimal))

    score = sum(scores) / len(scores)

    return {"score": score, "recommended": f"{optimal} sentences per intention"}


def evaluate_size_score(dataset):
    intentions = dataset["intentions"]

    intentions_size = len(intentions)
    if intentions_size < 2:
        return 0

    train_count = dataset["train_count"]
    evaluate_count = dataset["evaluate_count"]

    optimal = int(
        692.4702 + (-1.396326 - 692.4702) / (1 + (train_count / 5646.078) ** 0.7374176)
    )

    if evaluate_count >= optimal:
        score = 1.0
    else:
        score = score_cumulated(evaluate_count, optimal)

    return {"score": score, "recommended": f"{optimal} evaluation sentences"}


# TODO: word distribution score


def arrange_data(train_data, eval_data):
    """
        :param train_data: list of sentences {"intent";"text"}
        :param eval_data:  list of sentences {"intent";"text"}
        :return: formatted dataset
    """
    dataset = {
        "intentions": [],
        "train_count": len(train_data),
        "train": {},
        "evaluate_count": len(eval_data),
        "evaluate": {},
    }

    for data in train_data:
        if data["intent"] not in dataset["intentions"]:
            dataset["intentions"].append(data["intent"])
            dataset["train"][data["intent"]] = 0

        dataset["train"][data["intent"]] += 1

    for data in eval_data:
        if data["intent"] not in dataset["intentions"]:
            continue
        if data["intent"] not in dataset["evaluate"]:
            dataset["evaluate"][data["intent"]] = 0

        dataset["evaluate"][data["intent"]] += 1

    return dataset


def get_scores(repository_version, repository_authorization):

    train_data = (
        backend()
        .request_backend_get_examples(
            repository_version, False, None, repository_authorization
        )
        .get("results")
    )

    eval_data = backend().request_backend_start_evaluation(
        repository_version, repository_authorization
    )

    dataset = arrange_data(train_data, eval_data)

    scores = {
        "intentions_balance": intentions_balance_score(dataset),
        "intentions_size": intentions_size_score(dataset),
        "evaluate_size": evaluate_size_score(dataset),
    }

    sum = 0
    for n in scores.keys():
        sum += scores[n]["score"]
    average = sum / len(scores)

    scores["average"] = average

    return scores


def plot_func(func, optimal):

    x = np.linspace(0, 2 * optimal, 100)
    y = [func(n, optimal=optimal) for n in x]

    plt.plot(x, y)
    plt.plot([optimal, optimal], [0, 100])
    plt.ylabel("score")
    plt.xlabel("distance")
    plt.show()


if __name__ == "__main__":
    # Test examples:

    mocked_repository_example = {
        "intentions": ["a", "b", "c", "d", "e"],
        "train_count": 103,
        "train": {"a": 42, "b": 5, "c": 23, "d": 14, "e": 19},
        "evaluate_count": 29,
        "evaluate": {"a": 5, "b": 5, "c": 5, "d": 7, "e": 7},
    }

    plot_func(score_cumulated, optimal=50)
    plot_func(score_normal, optimal=50)

    test = intentions_balance_score(mocked_repository_example)
    print("Balance Score: ", test["score"], test["recommended"])

    test = intentions_size_score(mocked_repository_example)
    print("Number of training sentences Score: ", test["score"], test["recommended"])

    test = evaluate_size_score(mocked_repository_example)
    print("Number of evaluation sentences Score: ", test["score"], test["recommended"])
