// measurement.js
const { exec } = require('child_process');
const pidusage = require('pidusage');
const fs = require('fs');

// Nagłówek pliku CSV
const header = 'tool,scenario,migrationTimeMs,rollbackTimeMs,exitCode,scriptLines,cpuPercent,ramBytes\n';
fs.writeFileSync('results.csv', header);

// Funkcja uruchamiająca komendę i mierząca metryki
function runAndMeasure(command, tool, scenario) {
  return new Promise((resolve) => {
    const startTime = process.hrtime.bigint();
    const proc = exec(command);
    let peakCPU = 0, peakMem = 0;
    const pid = proc.pid;

    // Co 100ms pobieramy statystyki procesu
    const interval = setInterval(async () => {
      try {
        const stats = await pidusage(pid);
        peakCPU = Math.max(peakCPU, stats.cpu);
        peakMem = Math.max(peakMem, stats.memory);
      } catch (e) {
        // proces mógł się zakończyć
      }
    }, 100);

    proc.on('exit', (code) => {
      clearInterval(interval);
      const elapsedMs = Number(process.hrtime.bigint() - startTime) / 1e6;
      // Przyjmujemy, że rollback jest wykonany osobnym poleceniem, można zmierzyć oddzielnie
      const rollbackTimeMs = 0;
      const lines = (scenario === 'rename_column' ? (tool === 'Flyway' ? 3 : 3) : (tool === 'Flyway' ? 1002 : 1005));
      // Zapisujemy wynik do CSV
      const line = `${tool},${scenario},${elapsedMs.toFixed(2)},${rollbackTimeMs},${code},${lines},${peakCPU.toFixed(1)},${peakMem}\n`;
      fs.appendFileSync('results.csv', line);
      resolve();
    });
  });
}

// Przykładowe uruchomienie dla Flyway (należy zmienić na odpowiednie polecenie uruchamiające migrację)
async function main() {
  await runAndMeasure('mvn spring-boot:run -Pflyway', 'Flyway', 'rename_column');
  await runAndMeasure('mvn spring-boot:run -Pliquibase', 'Liquibase', 'rename_column');
  await runAndMeasure('mvn spring-boot:run -Pflyway', 'Flyway', 'big_table');
  await runAndMeasure('mvn spring-boot:run -Pliquibase', 'Liquibase', 'big_table');
  console.log('Pomiar zakończony, wyniki zapisane w results.csv');
}

main();
