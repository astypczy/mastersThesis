# Database Migration Tools in CI/CD Environments

This project compares **Flyway** and **Liquibase** as database migration management tools in CI/CD environments. It was developed as part of a master's thesis focused on evaluating their performance, reliability, and overall effectiveness.

## Project Overview

The project includes a demonstration application that allows users to execute database migrations and rollbacks using Flyway and Liquibase. It also provides a database schema preview and displays collected performance metrics.

The evaluation includes:
- Database migration and rollback execution using Flyway and Liquibase.
- Two CI/CD pipelines implemented with GitHub Actions.
- Performance measurements collected in both local and CI/CD environments.
- Statistical analysis of migration execution times.
- A multi-criteria model for evaluating the overall effectiveness of both tools.

## Effectiveness Evaluation Model

The project introduces a **multi-criteria model** for evaluating database migration tools. It combines normalized metrics covering:
- Migration execution time.
- Rollback execution time.
- Migration script complexity.
- CPU and RAM usage.
- Subjective assessment of the tool.
- Availability of rollback support in the free edition.

The model calculates separate effectiveness scores for local and CI/CD environments and combines them into a global score using a configurable weighting parameter:

<p align="center">
  <strong>E = α × E<sub>LOCAL</sub> + (1 − α) × E<sub>CI</sub></strong>
</p>

The parameter `α` determines the relative importance of the local environment compared to CI/CD. In the experiments, `α = 0.4`, assigning **40% weight to the local environment and 60% to CI/CD**.

This approach allows the evaluation to be adapted to different organizational priorities. When CI/CD is given greater importance (`α ≤ 0.2`), Flyway achieves a higher overall score.

## Results

The final effectiveness scores obtained in the experiments were:

| Tool | Global Effectiveness Score |
|---|---:|
| Flyway | 0.52 |
| Liquibase | 0.54 |

Liquibase achieved a slightly higher overall score under the selected weighting configuration. However, the results indicate that **there is no universally best tool**: the choice depends on the priorities and requirements of a given project. Flyway generally performed better in terms of execution time, while Liquibase offered advantages in implementation simplicity and built-in rollback support in its free edition.

## Technologies

- [Flyway](https://flywaydb.org/)
- [Liquibase](https://www.liquibase.com/)
- [GitHub Actions](https://github.com/features/actions)

---

# Narzędzia do migracji baz danych w środowiskach CI/CD

Projekt porównuje narzędzia **Flyway** i **Liquibase** wykorzystywane do zarządzania migracjami baz danych w środowiskach CI/CD. Został opracowany w ramach pracy magisterskiej poświęconej ocenie ich wydajności, niezawodności i ogólnej efektywności.

## Opis projektu

Projekt obejmuje aplikację demonstracyjną umożliwiającą wykonywanie migracji i rollbacków baz danych za pomocą Flyway i Liquibase. Aplikacja udostępnia również podgląd schematu bazy danych oraz prezentuje zebrane metryki wydajnościowe.

Zakres badań obejmuje:
- Wykonywanie migracji i rollbacków przy użyciu Flyway i Liquibase.
- Dwa pipeline’y CI/CD zrealizowane za pomocą GitHub Actions.
- Pomiary wydajności w środowisku lokalnym i CI/CD.
- Analizę statystyczną czasów wykonywania migracji.
- Wieloaspektowy model oceny efektywności obu narzędzi.

## Model oceny efektywności

W projekcie opracowano **wieloaspektowy model oceny** narzędzi do migracji baz danych. Uwzględnia on znormalizowane metryki obejmujące:
- Czas wykonywania migracji.
- Czas wykonywania rollbacku.
- Złożoność skryptów migracyjnych.
- Zużycie CPU i pamięci RAM.
- Subiektywną ocenę narzędzia.
- Dostępność mechanizmu rollbacku w darmowej wersji.

Model wyznacza osobne wskaźniki efektywności dla środowiska lokalnego i CI/CD, a następnie łączy je w globalny wynik za pomocą konfigurowalnego parametru wagowego:

<p align="center">
  <strong>E = α × E<sub>LOCAL</sub> + (1 − α) × E<sub>CI</sub></strong>
</p>

Parametr `α` określa względne znaczenie środowiska lokalnego w porównaniu z CI/CD. W przeprowadzonych badaniach przyjęto `α = 0,4`, co oznacza **wagę 40% dla środowiska lokalnego i 60% dla CI/CD**.

Model pozwala dostosować ocenę do priorytetów organizacji i specyfiki procesu wdrożeniowego. Przy większym znaczeniu CI/CD (`α ≤ 0,2`) wyższy wynik globalny uzyskuje Flyway.

## Wyniki

Końcowe wskaźniki efektywności uzyskane w badaniach wyniosły:

| Narzędzie | Globalny wskaźnik efektywności |
|---|---:|
| Flyway | 0,52 |
| Liquibase | 0,54 |

Przy przyjętych wagach nieco wyższy wynik uzyskał Liquibase. Wyniki wskazują jednak, że **nie istnieje jedno narzędzie najlepsze w każdym przypadku** — wybór zależy od priorytetów i wymagań danego projektu. Flyway na ogół osiągał krótsze czasy wykonywania operacji, natomiast Liquibase oferował korzyści związane z prostotą implementacji i wbudowaną obsługą rollbacków w darmowej wersji.

## Technologie

- [Flyway](https://flywaydb.org/)
- [Liquibase](https://www.liquibase.com/)
- [GitHub Actions](https://github.com/features/actions/)
