Program is developed in order to learn german vocabulary.
User provides list of words.
Program asks about words or articles and save number of correct or incorrect answers.
If correct answer number is bigger than incorrect answer number,
the word is claimed as learnt and will not be taken into consideration in next round.

Program read csv file with 8 columns:
- POLISH - polish work
- ARTICLE - article of german word
- SINGULAR - single form of german word
- PLURAL - plural form of german word
- ARTICLE_INCORRECT
- ARTICLE_CORRECT
- WORD_INCORRECT
- WORD_CORRECT

Program options:
ARTICLE_CORRECT_LIMIT=5     - for option 2 lines with (ARTICLE_CORRECT-ARTICLE_INCORRECT) more than this number will be ignored
WORD_CORRECT_LIMIT=5        - for option 1 lines with (WORD_CORRECT-WORD_INCORRECT) more than this number will be ignored

Option 1 - WORT:
- Program chose random line ( and check WORD_CORRECT_LIMIT) from data and show value for key "POLISH"
- User have to type german word
- if input is equal to value for key "SINGULAR" value "WORD_CORRECT"+1 and display "RICHTIG"
- if input is not equal to value for key "SINGULAR" value "WORD_INCORRECT"+1 and display "FALSCH"

Option 2 - ARTIKEL:
- Program chose random line ( and check ARTICLE_CORRECT_LIMIT) from data and show value for key "SINGULAR"
- User have to type german word
- if input is equal to value for key "SINGULAR" value "WORD_CORRECT"+1 and display "RICHTIG"
- if input is not equal to value for key "SINGULAR" value "WORD_INCORRECT"+1 and display "FALSCH"