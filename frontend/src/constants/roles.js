export function resolveDashboardByRole(role) {
  if (role === 'REITOR' || role === 'ADMIN') {
    return { name: 'dashboard-reitor' }
  }

  if (role === 'DIRETOR') {
    return { name: 'dashboard-diretor' }
  }

  if (role === 'CHEFE') {
    return { name: 'dashboard-chefe' }
  }

  return { name: 'login' }
}
