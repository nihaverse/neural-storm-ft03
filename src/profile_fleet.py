
import cProfile
import pstats
import time

from src.simulation import (
    load_simulation_data,
    FleetSimulationManager
)
from src.inference import load_models


def profile_fleet():

    print("Loading validation data...")
    df = load_simulation_data()

    print("Loading trained models...")
    models = load_models()

    print("Initializing fleet...")
    fleet = FleetSimulationManager(df=df, models=models)

    total_readings = len(df)
    processed_readings = 0

    start = time.perf_counter()

    while not fleet.is_finished:
        results = fleet.process_next_cycle()
        processed_readings += len(results)

    elapsed = time.perf_counter() - start

    print("\nFLEET PERFORMANCE")
    print("-----------------")
    print(f"Total readings: {processed_readings}")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Readings per second: {processed_readings / elapsed:.2f}")
    print(f"Expected readings: {total_readings}")


if __name__ == "__main__":

    profiler = cProfile.Profile()

    profiler.enable()
    profile_fleet()
    profiler.disable()

    print("\nTOP 20 FUNCTIONS BY CUMULATIVE TIME")
    print("-----------------------------------")

    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)
