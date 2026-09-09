# Decoupled IoT Event Streaming Architecture

## Overview
This capstone project demonstrates an enterprise-grade, event-driven architecture designed to solve a common IoT challenge: point-to-point data silos. By placing a Redpanda event broker at the center of the infrastructure, edge sensors are completely decoupled from downstream data consumers, allowing for infinite horizontal scalability and zero data loss during database maintenance.

Built with pre-sales engineering in mind, this project emphasizes **business value through technical architecture**, showcasing secure fan-out patterns, containerized orchestration, and real-time data visualization.

## Architecture & Data Flow

```mermaid
flowchart LR
    %% Define Nodes
    Sensors([IoT Sensors<br/>sensor.py])
    Broker{{"Redpanda Broker<br/>(Docker)"}}
    Topic[Topic:<br/>classroom-temperatures]
    Dashboard([Live Terminal<br/>dashboard.py])
    DBWriter([DB Writer<br/>db_writer.py])
    DB[(PostgreSQL<br/>(Docker))]
    UI[[Metabase UI<br/>(Docker)]]

    %% Define Flow
    Sensors -- Produces JSON --> Broker
    Broker --- Topic
    Topic -- Consumer Group 1 --> Dashboard
    Topic -- Consumer Group 2 --> DBWriter
    DBWriter -- SQL INSERT --> DB
    DB -- Queries --> UI

    %% Styling
    classDef python fill:#306998,color:#FFD43B,stroke:#306998
    classDef data fill:#336791,color:#fff,stroke:#336791
    classDef broker fill:#E34F26,color:#fff,stroke:#E34F26
    
    class Sensors,Dashboard,DBWriter python
    class DB,UI data
    class Broker broker
