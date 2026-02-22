export function resolveDashboardByRole(role) {
  if (role === 'REITOR') {
    return { name: 'dashboard-reitor' }
  }

  if (role === 'ADMIN') {
    return { name: 'dashboard-admin' }
  }

  if (role === 'DIRETOR') {
    return { name: 'dashboard-diretor' }
  }

  if (role === 'CHEFE') {
    return { name: 'dashboard-chefe' }
  }

  return { name: 'login' }
}
