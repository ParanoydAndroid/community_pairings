import argparse
import json
import math
from itertools import permutations
from statistics import mean
from typing import Dict, Iterable

PREFERENCES = {
    'Britta': {
        'Jeff': 4,
        'Todd': 2,
        'Annie': 1,
        'Pierce': 6,
        'Shirley': 7,
        'Abed': 3,
        'Troy': 5
    },
    'Jeff': {
        'Britta': 3,
        'Todd': 5,
        'Annie': 1,
        'Pierce': 6,
        'Shirley': 7,
        'Abed': 2,
        'Troy': 4
    },
    'Todd': {
        'Britta': 1,
        'Jeff': 1,
        'Annie': 1,
        'Pierce': 1,
        'Shirley': 1,
        'Abed': 1,
        'Troy': 1
    },
    'Annie': {
        'Britta': 5,
        'Jeff': 6,
        'Todd': 3,
        'Pierce': 4,
        'Shirley': 7,
        'Abed': 1,
        'Troy': 2
    },
    'Pierce': {
        'Britta': 5,
        'Jeff': 4,
        'Todd': 7,
        'Annie': 1,
        'Shirley': 6,
        'Abed': 2,
        'Troy': 3
    },
    'Shirley': {
        'Britta': 2,
        'Jeff': 4,
        'Todd': 3,
        'Annie': 5,
        'Pierce': 7,
        'Abed': 6,
        'Troy': 1
    },
    'Abed': {
        'Britta': 7,
        'Jeff': 4,
        'Todd': 2,
        'Annie': 3,
        'Pierce': 6,
        'Shirley': 5,
        'Troy': 1
    },
    'Troy': {
        'Britta': 6,
        'Jeff': 4,
        'Todd': 3,
        'Annie': 2,
        'Pierce': 7,
        'Shirley': 5,
        'Abed': 1,
    }
}


def main():
    args = _get_cli_args()
    if args.prefs is None:
        preferences = PREFERENCES

    else:
        with open(args.prefs, 'r') as f:
            preferences = json.load(f)

    if len(preferences) % 2 != 0:
        print('Cannot assign partners among an odd number of people.  Quitting.')
        return

    ranker = Ranker(preferences, args.metric, worst=args.britta)
    ranker.get_solutions()

    print(
        f'Final Score: {ranker.score:{ranker.format_string}}, achieved by {len(ranker.solutions)} possible pairings')

    for idx, solution in enumerate(ranker.solutions):
        print(f'Solution {idx}:')
        for first, second in solution:
            print(f'\t{"":17}{f"{first}" + ",":9} {second:9}')
            print(
                f'\tRank By Partner: {ranker.preferences[second][first]:^9}{ranker.preferences[first][second]:^9}\n')


class Ranker:
    '''Calculate the best lab partners under a variety of metrics.
    '''
    Preferences = Dict[str, Dict[str, int]]

    def __init__(self, preferences: Preferences, metric: str, **kwargs):
        self.preferences = preferences
        self.metric = metric

        self.worst = kwargs.get('worst', False)

        self.solutions = set()
        self.score = 0
        self.format_string = '.2f'

    def get_solutions(self):
        ''' Using the given metric and preferences, set the solution(s) to the pairings with the best score, 
         and additionally set the formatting string for display.
         '''

        # The audience appeal metric requires special handling because it's constructed, not searched for.
        if self.metric == 'appeal':
            self.solutions.add(self.get_audience_appeal())
            self.score = 'N/A'
            self.format_string = ''
            return

        # All non-appeal metrics test pairing-by-pairing
        self.score = math.inf
        self.format_string = '.2f'
        reverse = -1 if self.worst else 1
        for pairing in self.get_pairings():
            candidate_score = reverse * self.get_score(pairing)
            if candidate_score > self.score:
                continue

            elif candidate_score < self.score:
                self.score = candidate_score
                self.solutions = {pairing}

            else:
                self.solutions.add(pairing)

        self.score = reverse * self.score

    def get_audience_appeal(self) -> frozenset:
        ''' Returns the solution that pairs the most and least popular people.

        Must be uniquely handled because it's directly constructed instead of a search.
        '''
        popularity = []
        for member in self.preferences.keys():
            popularity.append((self._get_popularity(member), member))

        popularity = sorted(popularity)
        pairings = []
        for i in range(len(popularity)//2):
            first = popularity[i][1]
            second = popularity[-(i+1)][1]
            pairings.append(frozenset((first, second)))

        return frozenset(pairings)

    def _get_popularity(self, name: str) -> int:
        score = 0
        for k, v in self.preferences.items():
            if name == k:
                continue

            score += v[name]

        return score

    def get_score(self, pairings: frozenset) -> float:
        ''' Returns the score of all pairings by dispatching to various metric functions.  Does not
        handle audience appeal.
        '''
        if self.metric == 'total':
            return self._get_total_happiness(pairings)

        if self.metric == 'avg':
            return self._get_average_happiness(pairings)

        if self.metric == 'maximin':
            return self._get_maximin(pairings)

        else:
            raise Exception(
                'Invalid argument provided as metric.  Please use "avg", "total", "maximin" or "appeal"')

    def _get_total_happiness(self, pairings) -> float:
        ''' Metric calculated by the total sum of pairwise preference (lower is better).
        '''
        score = 0.0
        for first, second in pairings:
            score += self.preferences[first][second]
            score += self.preferences[second][first]

        return score

    def _get_average_happiness(self, pairings) -> float:
        ''' Metric calculating the average happiness across all pairs.
        '''
        averages = []
        for first, second in pairings:
            averages.append(
                mean((self.preferences[first][second],
                     self.preferences[second][first]))
            )

        return mean(averages)

    def _get_maximin(self, pairings) -> float:
        ''' Metric that returns the worst single pairing, and therefore minimizes the worst possible situation

        ... unless you Britta it, in which case it returns the pairing(s) with the worst single pair possible.
        '''
        worst = 0
        for first, second in pairings:
            score = self.preferences[first][second] + \
                self.preferences[second][first]
            worst = worst if worst > score else score

        return worst

    def get_pairings(self) -> Iterable:
        # In case you're wondering, we use frozensets everywhere because we want fast, order-agnostic inclusion checks,
        # but sets can't contain sets, so we use the immutable frozensets as hashable elements of the solutions set.

        iter = permutations(self.preferences.keys())
        for permutation in iter:
            pairings = []
            for i in range(0, len(permutation) - 1, 2):
                first = permutation[i]
                second = permutation[(i+1)]
                pairings.append(frozenset((first, second)))

            yield frozenset(pairings)


def _get_cli_args():
    parser = argparse.ArgumentParser(
        description="Calculate the best lab partners under a variety of metrics")
    parser.add_argument('--metric', '-m', default='appeal',
                        help='The metric used.  "Total", "avg", or "maximin" happiness')
    parser.add_argument('--britta', '-b', action='store_true',
                        help='If set, returns the worst pairings according to the given metric')
    parser.add_argument(
        '--prefs', '-p', default=None, help=f'Name of a file containing a JSON-formatted dictionary of group '
        'preference ballots. See example_ballot.json for a ballot, that is an example and, unexpectedly, is in json. '
        'Defaults to the global PREFERENCES variable in this script.')
    return parser.parse_args()


if __name__ == '__main__':
    main()
