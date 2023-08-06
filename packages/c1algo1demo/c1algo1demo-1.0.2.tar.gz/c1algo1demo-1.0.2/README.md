# algorithm-1

# Usage

Install the latest release via `pip install c1algo1`

Example package usage:

```python
from c1algo1 import scheduler
schedule = scheduler.generate_schedule(schedule_input)
```

# Testing

Automated tests are located in the `testing/`directory, and can be run with `pytest`from that same directory.

Example test output:

```bash
============================= test session starts ==============================
platform darwin -- Python 3.10.4, pytest-7.1.2, pluggy-1.0.0
cachedir: .pytest_cache
collected 3 items

test_preprocessing.py::test_associate_all_courses PASSED                 [ 33%]
test_preprocessing.py::test_sort_courses_by_interest PASSED              [ 66%]
test_scheduler.py::test_scheduler PASSED                                 [100%]

============================== 3 passed in 0.07s ===============================
```


# Brett Demo

Branch and bound demo: Run test_assign_professors... whatever its called.

Pass in a year to generate_schedule to use historical data (WARNING: will run for 24 hours and eat all your memory before crashing)

Output is the tree structure with each path to a leaf being an optimal solution.

Number of solutions returned can be changed using the solution_limit variable, currently 10.
