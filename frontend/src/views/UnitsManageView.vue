<template>
  <main class="admin-layout units-layout">
    <SideNav />

    <section class="content-area units-content">
      <header class="units-topbar">
        <div class="units-tenant">Restauro Admin</div>
        <DashboardUserMenu />
      </header>

      <h1 class="units-title">Gerir Unidades Orgânicas</h1>
      <p class="units-subtitle">Gestão e atualização das Unidades Orgânicas</p>

      <section class="units-card">
        <div class="units-toolbar">
          <div class="units-search">
            <span class="units-search-icon"></span>
            <input v-model="searchTerm" placeholder="Pesquisar por nome ou código" />
          </div>
          <div class="units-actions">
            <button class="btn btn-primary units-btn" @click="listUnits">+ Atualizar Lista</button>
            <router-link class="btn btn-ghost units-btn" to="/units/create">+ Nova Unidade Orgânica</router-link>
          </div>
        </div>

        <div class="units-table">
          <table>
            <thead>
              <tr>
                <th @click="toggleSort('id')">ID</th>
                <th @click="toggleSort('name')">Nome</th>
                <th @click="toggleSort('code')">Código</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedItems" :key="item.id">
                <td>{{ item.id }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.code }}</td>
                <td>
                  <div class="units-actions-cell">
                    <button class="btn btn-primary btn-small" @click="selectForEdit(item)">Editar</button>
                    <button class="units-dots" type="button">⋮</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="units-pagination" v-if="filteredItems.length">
          <button class="btn btn-ghost" @click="prevPage" :disabled="currentPage===1">Anterior</button>
          <span>Página {{ currentPage }} de {{ totalPages }}</span>
          <button class="btn btn-ghost" @click="nextPage" :disabled="currentPage>=totalPages">Próxima</button>
        </div>
      </section>

      <section v-if="selectedItem" class="units-card units-edit-card">
        <h3>Atualizar Unidade: {{ selectedItem.name }}</h3>
        <form class="units-form" @submit.prevent="updateUnit">
          <input v-model="updateForm.name" placeholder="Nome" />
          <input v-model="updateForm.code" placeholder="Código" />
          <input v-model="updateForm.description" placeholder="Descrição" />
          <button class="btn btn-primary" type="submit">Salvar Atualização</button>
        </form>
      </section>

      <p class="success units-message" v-if="successMessage">{{ successMessage }}</p>
      <p class="error units-message" v-if="errorMessage">{{ errorMessage }}</p>
    </section>
  </main>
</template>
<script setup>
import axios from 'axios'; import { computed, onMounted, reactive, ref, watch } from 'vue'
import DashboardUserMenu from '../components/DashboardUserMenu.vue'
import SideNav from '../components/SideNav.vue'; import api from '../services/api'
const items=ref([]), selectedItem=ref(null), searchTerm=ref(''), currentPage=ref(1), successMessage=ref(''), errorMessage=ref(''), sortBy=ref('id'), sortDir=ref('asc'); const pageSize=6
const updateForm=reactive({ name:'', code:'', description:'' })
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
const filteredItems=computed(()=>{const q=searchTerm.value.trim().toLowerCase(); if(!q) return items.value; return items.value.filter(i=>`${i.name} ${i.code}`.toLowerCase().includes(q))})
const sortedItems=computed(()=>{const list=[...filteredItems.value]; const k=sortBy.value; const d=sortDir.value==='asc'?1:-1; return list.sort((a,b)=> (typeof a[k]==='number'&&typeof b[k]==='number'?a[k]-b[k]:String(a[k]??'').localeCompare(String(b[k]??'')))*d)})
const totalPages=computed(()=>Math.max(1,Math.ceil(filteredItems.value.length/pageSize))); const paginatedItems=computed(()=>sortedItems.value.slice((currentPage.value-1)*pageSize,(currentPage.value-1)*pageSize+pageSize))
watch(searchTerm,()=>currentPage.value=1)
const prevPage=()=>{if(currentPage.value>1)currentPage.value--}; const nextPage=()=>{if(currentPage.value<totalPages.value)currentPage.value++}
const toggleSort=(c)=>{if(sortBy.value===c)sortDir.value=sortDir.value==='asc'?'desc':'asc'; else{sortBy.value=c; sortDir.value='asc'}}
async function listUnits(){ try{successMessage.value=''; errorMessage.value=''; const r=await api.get('/api/units'); items.value=r.data }catch(e){ errorMessage.value=err(e) }}
function selectForEdit(item){ selectedItem.value=item; updateForm.name=item.name; updateForm.code=item.code; updateForm.description=item.description||'' }
async function updateUnit(){ try{successMessage.value=''; errorMessage.value=''; const p={}; if(updateForm.name) p.name=updateForm.name; if(updateForm.code) p.code=updateForm.code; if(updateForm.description) p.description=updateForm.description; await api.put(`/api/units/${selectedItem.value.id}`, p); successMessage.value='Unidade atualizada com sucesso.'; await listUnits() }catch(e){ errorMessage.value=err(e) }}
onMounted(listUnits)
</script>
