def shuffle(
    ctx,
    sample_metadata,
    case_control_column,
    categories,
    case_identifier,
    tolerances=None,
    on_match_failure="raise",
    iterations=10,
    strict=True,
    n_jobs=1,
):
    match_one_to_many = ctx.get_action("qupid", "match_one_to_many")
    match_one_to_one = ctx.get_action("qupid", "match_one_to_one")

    results = []
    cm_one_to_many, = match_one_to_many(
        sample_metadata=sample_metadata,
        case_control_column=case_control_column,
        categories=categories,
        case_identifier=case_identifier,
        tolerances=tolerances,
        on_failure=on_match_failure
    )
    results.append(cm_one_to_many)

    cm_collection, = match_one_to_one(
        case_match_one_to_many=cm_one_to_many,
        iterations=iterations,
        strict=strict,
        n_jobs=n_jobs
    )
    results.append(cm_collection)

    return tuple(results)
