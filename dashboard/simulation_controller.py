import streamlit as st


def advance_fleet_one_tick(cycles_per_tick=1):
    """Advance shared fleet state by the requested number of cycles."""

    fleet_manager = st.session_state["fleet_manager"]

    from state import update_engine_state

    for _ in range(cycles_per_tick):
        if fleet_manager.is_finished:
            break

        cycle_results = fleet_manager.process_next_cycle()

        for engine_id, result in cycle_results.items():
            update_engine_state(
                engine_id=engine_id,
                cycle=result["cycle"],
                prediction=result["prediction"]
            )


def get_simulation_progress(total_cycles):
    engine_states = st.session_state["engine_states"]

    completed_cycles = sum(
        engine.get("current_cycle", engine.get("cycle", 0))
        for engine in engine_states.values()
    )

    progress = min(completed_cycles / max(total_cycles, 1), 1.0)

    return completed_cycles, progress



def run_live_page(render_page, total_cycles):

    tick_interval = 0.25

    run_interval = (
        tick_interval
        if st.session_state["simulation_running"]
        and not st.session_state["fleet_manager"].is_finished
        else None
    )

    @st.fragment(run_every=run_interval)
    def simulation_fragment():

        fleet_manager = st.session_state["fleet_manager"]

        # 1. Handle completion before rendering.
        if fleet_manager.is_finished:

            if st.session_state.get("simulation_status") != "Completed":
                st.session_state["simulation_running"] = False
                st.session_state["simulation_status"] = "Completed"
                st.rerun(scope="app")

        # 2. Calculate progress from the current committed state.
        completed_cycles, progress = get_simulation_progress(
            total_cycles
        )

        tick_count = st.session_state.get(
            "simulation_tick_count", 0
        )

        st.session_state["refresh_histogram"] = (
            tick_count % 3 == 0
            or fleet_manager.is_finished
            or "cached_rul_histogram" not in st.session_state
        )

        # 3. Render the complete dashboard FIRST.
        st.progress(
            progress,
            text=(
                f"Simulation Progress: {completed_cycles} / "
                f"{total_cycles} cycles"
            )
        )

        render_page()

        # 4. Advance simulation AFTER rendering.
        if (
            st.session_state["simulation_running"]
            and not fleet_manager.is_finished
        ):

            speed = float(
                st.session_state["simulation_speed"]
            )

            cycles_per_tick = max(
                1,
                int(round(speed * 5))
            )

            advance_fleet_one_tick(
                cycles_per_tick=cycles_per_tick
            )

            st.session_state["simulation_tick_count"] = (
                tick_count + 1
            )

        # 5. Refresh the full app when simulation completes.
        if fleet_manager.is_finished:

            st.session_state["simulation_running"] = False
            st.session_state["simulation_status"] = "Completed"

            st.rerun(scope="app")

    simulation_fragment()
