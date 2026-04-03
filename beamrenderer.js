function renderBeam(session) {
  const total = 20;
  const filled = Math.floor(((session.beamPosition + 100) / 200) * total);
  const empty = total - filled;

  return `
⚡ BEAM STRUGGLE ⚡

${"█".repeat(filled)}${"░".repeat(empty)}

Position: ${session.beamPosition}
Momentum: x${session.momentum.toFixed(2)}
`;
}

module.exports = { renderBeam };
