"""Interactive skill loading should be deliberate, not a keyword fan-out."""


def _write_skill(root):
    skill = root / "software-development" / "systematic-debugging"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: systematic-debugging\n"
        "description: Reproduce and root-cause defects before fixing them.\n"
        "---\n"
        "Body.\n",
        encoding="utf-8",
    )


def test_interactive_prompt_loads_one_intent_matched_skill(tmp_path, monkeypatch):
    from agent import prompt_builder as pb

    # Pin the interactive path: a single-query session marker (HERMES_SINGLE_QUERY_SESSION)
    # would otherwise switch the render to the one-shot variant.
    monkeypatch.delenv("HERMES_SINGLE_QUERY_SESSION", raising=False)
    _write_skill(tmp_path)
    pb.clear_skills_system_prompt_cache()
    prompt = pb.build_skills_system_prompt(skills_dir_override=tmp_path)

    assert "load the single best-matching skill first." in prompt
    assert "Do not load adjacent skills for later phases." in prompt
    assert "even partially relevant" not in prompt
    assert "Err on the side of loading" not in prompt
    assert "<available_skills>" in prompt
    assert "offer to save as a skill" in prompt


def test_one_shot_guidance_is_unchanged(tmp_path, monkeypatch):
    from agent import prompt_builder as pb
    from agent.oneshot_footprint import ONESHOT_SKILLS_LOAD_GUIDANCE

    _write_skill(tmp_path)
    monkeypatch.setattr(
        "agent.oneshot_footprint.is_single_query_session", lambda: True
    )
    pb.clear_skills_system_prompt_cache()
    prompt = pb.build_skills_system_prompt(skills_dir_override=tmp_path)

    assert ONESHOT_SKILLS_LOAD_GUIDANCE in prompt
    assert "Load the single best-matching skill first." not in prompt
