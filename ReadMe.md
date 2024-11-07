# Compile

This project supports compiling jobs and routines from a given project in DataStage On-Premise.

## Supported ETL Versions
- DataStage Infosphere 11.7
- DataStage Infosphere 11.5

## Supported Assets
- **Job Types**:
  - Parallel Job
  - Sequence Job
  - Server Job
- Routine

## Project Structure

- **config/**: Contains the configuration file.
- **input/**: Contains a text file specifying the asset type and asset name (e.g., `"job,job1"`).
- **bin/**: Contains the code for the compilation process.

## Output

After running the code, a **status/** folder will be created. This folder contains the respective project status file, which provides the status of the run.