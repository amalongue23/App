<template>
  <main class="admin-layout">
    <SideNav />
    <section class="content-area"><section class="ops-card">
    <OperationsNav title="Gestão de Departamentos" subtitle="Listagem e atualização em tela separada" />
    <div class="ops-toolbar"><button class="btn btn-ghost" @click="listAll">Atualizar Lista</button><select v-model.number="unitFilterId" @change="listByUnit"><option :value="0">Todas unidades</option><option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option></select><input v-model="searchTerm" placeholder="Filtrar por nome/código" /></div>
    <div class="ops-table-wrap"><table><thead><tr><th @click="toggleSort('id')">ID</th><th @click="toggleSort('name')">Nome</th><th @click="toggleSort('code')">Código</th><th @click="toggleSort('unit_id')">Unidade</th><th>Ações</th></tr></thead><tbody><tr v-for="item in paginatedItems" :key="item.id"><td>{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.code }}</td><td>{{ unitName(item.unit_id) }}</td><td><button class="btn btn-ghost" @click="selectForEdit(item)">Editar</button></td></tr></tbody></table></div>
    <div class="ops-pagination" v-if="filteredItems.length"><button class="btn btn-ghost" @click="prevPage" :disabled="currentPage===1">Anterior</button><span>Página {{ currentPage }} de {{ totalPages }}</span><button class="btn btn-ghost" @click="nextPage" :disabled="currentPage>=totalPages">Próxima</button></div>

    <article v-if="selectedItem" class="ops-edit-box"><h3>Atualizar Departamento: {{ selectedItem.name }}</h3><form class="ops-form" @submit.prevent="updateDepartment"><input v-model="updateForm.name" placeholder="Nome" /><input v-model="updateForm.code" placeholder="Código" /><select v-model.number="updateForm.unit_id"><option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option></select><button class="btn btn-primary" type="submit">Salvar Atualização</button></form></article>

    <p class="success" v-if="successMessage">{{ successMessage }}</p><p class="error" v-if="errorMessage">{{ errorMessage }}</p>
  </section></section></main>
</template>
<script setup>
import axios from 'axios'; import { computed, onMounted, reactive, ref, watch } from 'vue'
import OperationsNav from '../components/OperationsNav.vue'; import SideNav from '../components/SideNav.vue'; import api from '../services/api'
const items=ref([]), units=ref([]), selectedItem=ref(null), successMessage=ref(''), errorMessage=ref(''), unitFilterId=ref(0), searchTerm=ref(''), currentPage=ref(1), sortBy=ref('id'), sortDir=ref('asc'); const pageSize=6
const updateForm=reactive({ name:'', code:'', unit_id:0 })
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
const filteredItems=computed(()=>{const q=searchTerm.value.trim().toLowerCase(); if(!q)return items.value; return items.value.filter(i=>`${i.name} ${i.code}`.toLowerCase().includes(q))})
const sortedItems=computed(()=>{const list=[...filteredItems.value]; const k=sortBy.value; const d=sortDir.value==='asc'?1:-1; return list.sort((a,b)=>(typeof a[k]==='number'&&typeof b[k]==='number'?a[k]-b[k]:String(a[k]??'').localeCompare(String(b[k]??'')))*d)})
const totalPages=computed(()=>Math.max(1,Math.ceil(filteredItems.value.length/pageSize))); const paginatedItems=computed(()=>sortedItems.value.slice((currentPage.value-1)*pageSize,(currentPage.value-1)*pageSize+pageSize))
watch(searchTerm,()=>currentPage.value=1)
const prevPage=()=>{if(currentPage.value>1)currentPage.value--}; const nextPage=()=>{if(currentPage.value<totalPages.value)currentPage.value++}
const toggleSort=(c)=>{if(sortBy.value===c)sortDir.value=sortDir.value==='asc'?'desc':'asc'; else{sortBy.value=c; sortDir.value='asc'}}
const unitName=(id)=>units.value.find(u=>u.id===id)?.name||id
async function loadUnits(){ const r=await api.get('/api/units'); units.value=r.data }
async function listAll(){ const r=await api.get('/api/departments'); items.value=r.data }
async function listByUnit(){ try{ if(!unitFilterId.value){ await listAll(); return } const r=await api.get(`/api/departments/by-unit/${unitFilterId.value}`); items.value=r.data }catch(e){errorMessage.value=err(e)} }
function selectForEdit(item){ selectedItem.value=item; updateForm.name=item.name; updateForm.code=item.code; updateForm.unit_id=item.unit_id }
async function updateDepartment(){ try{successMessage.value=''; errorMessage.value=''; const payload={}; if(updateForm.name)payload.name=updateForm.name; if(updateForm.code)payload.code=updateForm.code; if(updateForm.unit_id)payload.unit_id=updateForm.unit_id; await api.put(`/api/departments/${selectedItem.value.id}`,payload); successMessage.value='Departamento atualizado com sucesso.'; await listByUnit() }catch(e){errorMessage.value=err(e)} }
onMounted(async()=>{try{await loadUnits(); await listAll()}catch(e){errorMessage.value=err(e)}})
</script>
