Inspired by s03e03 of Community, this console python program consumes votes from group members denoting their
parterning preference and returns the best (or worst) lab partner pairings.

Run `python community_pairings.py --help` for help information, some of which is reproduced below.

# Input:

A PREFERENCES environment variable is already defined in the script, and can be used by default or edited to reflect your voting ideas.

Alternatively, the ballot can be defined in a json file and passed into the script, see Flags below.

# Flags:

-   --metric, -m: Defines the metric by which we determine the "best" pairings. Currently supports 'avg', 'total', 'maximin', and 'appeal'. Because most metrics depend on rankings, lower is normally better (e.g. usually the better pairing is between two partners who ranked each other as their number 1 pick as opposed to number 7 picks).

    -   avg: Returns the pairings with the lowest average score.
    -   total: Returns the pairings with the lower total score.
    -   maximin: Returns the pairings where the worst pairing involved is as good as it can be. In other words, maximizes the minimum happiness someone could end up with in their pairing.
    -   appeal: Based on Abed's technique, pairs the most and least popular people together. The provided PREFERENCES config is already set up so that appeal returns the same pairings seen in the show.

-   --britta, -b: If you want to britta the pairings, just pass this flag in. Reverses the scoring system so that the
    metrics return the worst possible pairing under their scoring system. E.g. a britta flag on the maximin metric
    will return whichever pairings involve the worst possible pair of lab partners. Does not apply to the appeal metric.

-   --prefs, -p: A file name containing a JSON ballot. See the example_ballot.json file for the ballot format.

# Examples:

-   Get the pairings with the best total score (the mutual rankings between all partners sum to the lowest value possible): `python community_pairings.py -m total`

-   Get the pairings with the best average score: `python community_pairings.py -m avg`

-   Get the pairings with the most total unhappiness: `python community_pairings.py --metric total --britta`

-   Use your own ballot file to see how audience appeal would pair the group up: `python community_pairings.py -m appeal --prefs example_ballot.json` (obviously swap the file name or replace the contents of example_ballot.json)

-   Use your own ballot file to define the ballots and then try to make everyone as happy as you can ... but accidentally britta it: `python community_pairings.py -m total -b -p example_ballot.json`
