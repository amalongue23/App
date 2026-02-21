import { createRouter, createWebHistory } from 'vue-router'

import { resolveDashboardByRole } from '../constants/roles'
import AcademicYearsView from '../views/AcademicYearsView.vue'
import ChiefDashboardView from '../views/ChiefDashboardView.vue'
import CoursesCreateView from '../views/CoursesCreateView.vue'
import CoursesManageView from '../views/CoursesManageView.vue'
import CrudHomeView from '../views/CrudHomeView.vue'
import DatasetToolsView from '../views/DatasetToolsView.vue'
import DepartmentsCreateView from '../views/DepartmentsCreateView.vue'
import DepartmentsManageView from '../views/DepartmentsManageView.vue'
import DashboardView from '../views/DashboardView.vue'
import DirectorDashboardView from '../views/DirectorDashboardView.vue'
import LoginView from '../views/LoginView.vue'
import ReportsView from '../views/ReportsView.vue'
import StatisticsView from '../views/StatisticsView.vue'
import StudentsCreateView from '../views/StudentsCreateView.vue'
import StudentsManageView from '../views/StudentsManageView.vue'
import StudentStatusView from '../views/StudentStatusView.vue'
import UnitsCreateView from '../views/UnitsCreateView.vue'
import UnitsManageView from '../views/UnitsManageView.vue'
import UsersView from '../views/UsersView.vue'
import UserDetailView from '../views/UserDetailView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    {
      path: '/dashboard',
      name: 'dashboard',
      redirect: () => {
        const authStore = useAuthStore()
        authStore.restoreSession()
        return resolveDashboardByRole(authStore.user?.role)
      },
      meta: { requiresAuth: true },
    },
    { path: '/dashboard/reitor', name: 'dashboard-reitor', component: DashboardView, meta: { requiresAuth: true, roles: ['REITOR', 'ADMIN'] } },
    { path: '/dashboard/chefe', name: 'dashboard-chefe', component: ChiefDashboardView, meta: { requiresAuth: true, roles: ['CHEFE'] } },
    { path: '/dashboard/diretor', name: 'dashboard-diretor', component: DirectorDashboardView, meta: { requiresAuth: true, roles: ['DIRETOR'] } },

    { path: '/operations', name: 'operations', component: CrudHomeView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'CHEFE', 'ADMIN'] } },
    { path: '/statistics', name: 'statistics', component: StatisticsView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'CHEFE', 'ADMIN'] } },
    { path: '/academic-years', name: 'academic-years', component: AcademicYearsView, meta: { requiresAuth: true, roles: ['REITOR', 'ADMIN'] } },
    { path: '/users', name: 'users', component: UsersView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'ADMIN'] } },
    { path: '/users/:id', name: 'user-detail', component: UserDetailView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'ADMIN'] } },

    { path: '/units/create', name: 'units-create', component: UnitsCreateView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'ADMIN'] } },
    { path: '/units/manage', name: 'units-manage', component: UnitsManageView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'ADMIN'] } },

    { path: '/departments/create', name: 'departments-create', component: DepartmentsCreateView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
    { path: '/departments/manage', name: 'departments-manage', component: DepartmentsManageView, meta: { requiresAuth: true, roles: ['ADMIN'] } },

    { path: '/courses/create', name: 'courses-create', component: CoursesCreateView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'CHEFE', 'ADMIN'] } },
    { path: '/courses/manage', name: 'courses-manage', component: CoursesManageView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'CHEFE', 'ADMIN'] } },

    { path: '/students/create', name: 'students-create', component: StudentsCreateView, meta: { requiresAuth: true, roles: ['CHEFE', 'ADMIN'] } },
    { path: '/students/manage', name: 'students-manage', component: StudentsManageView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'CHEFE', 'ADMIN'] } },
    { path: '/students/:id/status', name: 'student-status', component: StudentStatusView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'CHEFE', 'ADMIN'] } },

    { path: '/datasets', name: 'datasets', component: DatasetToolsView, meta: { requiresAuth: true, roles: ['REITOR', 'ADMIN'] } },
    { path: '/reports', name: 'reports', component: ReportsView, meta: { requiresAuth: true, roles: ['REITOR', 'DIRETOR', 'ADMIN'] } },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  authStore.restoreSession()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) return { name: 'login' }

  if (to.meta.roles?.length) {
    const userRole = authStore.user?.role
    if (!userRole || !to.meta.roles.includes(userRole)) {
      authStore.logout()
      return { name: 'login' }
    }
  }

  if (to.name === 'login' && authStore.isAuthenticated) return resolveDashboardByRole(authStore.user?.role)

  return true
})

export default router
