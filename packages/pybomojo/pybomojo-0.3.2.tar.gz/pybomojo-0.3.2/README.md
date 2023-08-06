# pybomojo

A Python client for boxofficemojo.com

## API

Methods just return raw lists and dicts, because I don't need no fancy classes.

```python
from pybomojo import search_movies, get_box_office

search_movies('The Dark Knight')
# [
#   {
#     "exact": true, 
#     "movie_id": "tt0468569", 
#     "title": "The Dark Knight"
#   }, 
#   {
#     "exact": false, 
#     "movie_id": "tt1345836", 
#     "title": "The Dark Knight Rises"
#   }
# ]

get_box_office('tt0468569')
# {
#     'title': 'The Dark Knight (2008)',
#     'href': 'https://www.boxofficemojo.com/title/tt0468569',
#     'box_office': [
#         {
#             'gross': 67165092,
#             'cumulative': 67165092,
#             'rank': 1,
#             'theaters': 4366,
#             'date': 'Jul 18, 2008',
#             'day': 'Friday'
#         },
#         {
#             'gross': 47650240,
#             'cumulative': 114815332,
#             'rank': 1,
#             'theaters': 4366,
#             'date': 'Jul 19, 2008',
#             'day': 'Saturday'
#         },
#         {
#             'gross': 43596151,
#             'cumulative': 158411483,
#             'rank': 1,
#             'theaters': 4366,
#             'date': 'Jul 20, 2008',
#             'day': "Sunday"
#         },
#         # ...
#     ]
# }
```
