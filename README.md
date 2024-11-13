# Spotify Data Pipeline ETL Project

This repository contains an ETL (Extract, Transform, Load) data pipeline built on AWS to collect, process, and analyze song data from the Spotify API. The project leverages various AWS services to automate the entire data flow, making it easy to query and analyze the data using SQL in Amazon Athena.

## Project Structure

![Spotify Data Pipeline ETL Project](https://github.com/user-attachments/assets/59f234d3-9253-4ba8-850d-f3c9c6f995ce)


### Overview

1.  **Extract**: A Lambda function connects to the Spotify API to extract song data and stores the raw data in Amazon S3.
2.  **Transform**: A second Lambda function processes the raw data, performing necessary transformations and storing the transformed data back in S3.
3.  **Load**: AWS Glue catalogs the data, and Amazon Athena provides an interface for querying the processed data using SQL.

## Features

-   **Automated Data Extraction**: Scheduled using AWS CloudWatch to trigger the ETL pipeline at a set frequency.
-   **Data Transformation**: Raw data from Spotify is cleaned and transformed to a structured format.
-   **Data Cataloging and Querying**: AWS Glue catalogs the data, enabling SQL queries on the processed data through Amazon Athena.

## Technologies Used

-   **AWS Lambda**: For serverless data extraction and transformation.
-   **Amazon S3**: Storage for raw and transformed data.
-   **AWS Glue**: Data cataloging for structured data in S3.
-   **Amazon Athena**: Query engine for analyzing data with SQL.
-   **Spotify API**: Source of the song, album, and artist data.

## Getting Started

### Prerequisites

-   AWS account with permissions to create Lambda functions, S3 buckets, Glue crawlers, and Athena tables.
-   Spotify Developer account and API credentials (client ID and client secret).

### Installation

1.  **Clone this repository**:

```bash
    git clone https://github.com/gnavarrolema/ETL-Data-Pipeline-for-Spotify-on-AWS.git
    cd ETL-Data-Pipeline-for-Spotify-on-AWS
```
2.  **Set up AWS Services**:
    -   Create two Lambda functions:
        -   **Data Extraction Function**: Connects to Spotify API and saves raw data in S3.
        -   **Data Transformation Function**: Processes and restructures the data in S3.
    -   Configure AWS Glue for data cataloging and set up a Crawler to automate schema inference.
    -   Set up Amazon Athena to query the processed data.
3.  **Configure IAM Roles**:
    -   **Data Extraction Lambda**: Ensure it has permissions to write to S3 and log to CloudWatch.
    -   **Data Transformation Lambda**: Grant permissions for S3 read/write, CloudWatch logging, and Glue Crawler (if needed).

### Environment Variables

Set up the following environment variables in your Lambda functions for Spotify API access:

-   `SPOTIFY_CLIENT_ID`: Your Spotify API client ID.
-   `SPOTIFY_CLIENT_SECRET`: Your Spotify API client secret.

### Usage

1.  **Run the Pipeline**:
    -   Trigger the data extraction function (manually or by scheduling with CloudWatch).
    -   The transformation function will automatically process the data stored in S3.
    -   Glue will catalog the data, making it available for queries in Athena.
2.  **Query the Data in Athena**:
    -   Access Amazon Athena and query the `spotify_db` database to analyze song data.
    -   Example Query:

```sql
        SELECT * FROM spotify_db.songs_data LIMIT 10;
```
## Example Queries

Here are some example queries you can run in Athena:

-   **Top 10 Most Popular Songs**:

```sql
    SELECT song_name, popularity FROM spotify_db.songs_data ORDER BY popularity DESC LIMIT 10;
```
-   **Average Song Duration by Artist**:

```sql
    SELECT artist_id, AVG(duration_ms) AS avg_duration FROM spotify_db.songs_data GROUP BY artist_id ORDER BY avg_duration DESC;
```
## Future Enhancements

-   Add error handling and logging improvements.
-   Integrate with a dashboarding tool like Amazon QuickSight for data visualization.
-   Expand the pipeline to include additional data sources or more complex transformations.
