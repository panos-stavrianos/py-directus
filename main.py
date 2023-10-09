from py_directus.filter import F


if __name__ == "__main__":
    q1 = F(pools__name__eq="panos", hair__eq="brown")
    q2 = F(age__starts_with=23)
    q3 = F(job="programmer")

    combined_query = q1 | q3 | q3 | q2

    combined_query.print_explanation()
