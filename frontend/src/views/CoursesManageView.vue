<template>
  <main class="admin-layout">
    <SideNav />
    <section class="content-area"><section class="ops-card">
    <OperationsNav title="Gestão de Cursos" subtitle="Listagem e atualização em tela separada" />
    <div class="ops-toolbar"><select v-model.number="departmentFilterId" @change="listByDepartment"><option :value="0" disabled>Selecione o Departamento</option><option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option></select><input v-model="searchTerm" placeholder="Filtrar por nome/código" /></div>
    <div class="ops-table-wrap"><table><thead><tr><th @click="toggleSort('id')">ID</th><th @click="toggleSort('name')">Nome</th><th @click="toggleSort('code')">Código</th><th @click="toggleSort('credits')">Créditos</th><th>Ações</th></tr></thead><tbody><tr v-for="item in paginatedItems" :key="item.id"><td>{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.code }}</td><td>{{ item.credits }}</td><td><button class="btn btn-ghost" @click="selectForEdit(item)">Editar</button></td></tr></tbody></table></div>
    <div class="ops-pagination" v-if="filteredItems.length"><button class="btn btn-ghost" @click="prevPage" :disabled="currentPage===1">Anterior</button><span>Página {{ currentPage }} de {{ totalPages }}</span><button class="btn btn-ghost" @click="nextPage" :disabled="currentPage>=totalPages">Próxima</button></div>

    <article v-if="selectedItem" class="ops-edit-box"><h3>Atualizar Curso: {{ selectedItem.name }}</h3><form class="ops-form" @submit.prevent="updateCourse"><input v-model="updateForm.name" placeholder="Nome" /><input v-model="updateForm.code" placeholder="Código" /><select v-model.number="updateForm.department_id"><option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option></select><input v-model.number="updateForm.credits" type="number" min="0" placeholder="Créditos" /><button class="btn btn-primary" type="submit">Salvar Atualização</button></form></article>

    <p class="success" v-if="successMessage">{{ successMessage }}</p><p class="error" v-if="errorMessage">{{ errorMessage }}</p>
  </section></section></main>
</template>
<script setup>
import axios from 'axios'; import { computed, onMounted, reactive, ref, watch } from 'vue'
import OperationsNav from '../components/OperationsNav.vue'; import SideNav from '../components/SideNav.vue'; import api from '../services/api'
const departments=ref([]), items=ref([]), selectedItem=ref(null), successMessage=ref(''), errorMessage=ref(''), departmentFilterId=ref(0), searchTerm=ref(''), currentPage=ref(1), sortBy=ref('id'), sortDir=ref('asc'); const pageSize=6
const updateForm=reactive({ name:'', code:'', department_id:0, credits:0 })
const err=(e)=>axios.isAxiosError(e)?(e.response?.data?.message||'Erro na operação.'):'Erro na operação.'
const filteredItems=computed(()=>{const q=searchTerm.value.trim().toLowerCase(); if(!q)return items.value; return items.value.filter(i=>`${i.name} ${i.code}`.toLowerCase().includes(q))})
const sortedItems=computed(()=>{const list=[...filteredItems.value]; const k=sortBy.value; const d=sortDir.value==='asc'?1:-1; return list.sort((a,b)=>(typeof a[k]==='number'&&typeof b[k]==='number'?a[k]-b[k]:String(a[k]??'').localeCompare(String(b[k]??'')))*d)})
const totalPages=computed(()=>Math.max(1,Math.ceil(filteredItems.value.length/pageSize))); const paginatedItems=computed(()=>sortedItems.value.slice((currentPage.value-1)*pageSize,(currentPage.value-1)*pageSize+pageSize))
watch(searchTerm,()=>currentPage.value=1)
const prevPage=()=>{if(currentPage.value>1)currentPage.value--}; const nextPage=()=>{if(currentPage.value<totalPages.value)currentPage.value++}
const toggleSort=(c)=>{if(sortBy.value===c)sortDir.value=sortDir.value==='asc'?'desc':'asc'; else{sortBy.value=c; sortDir.value='asc'}}
async function loadDepartments(){ const r=await api.get('/api/departments'); departments.value=r.data; if(!departmentFilterId.value&&departments.value.length) departmentFilterId.value=departments.value[0].id }
async function listByDepartment(){ try{ if(!departmentFilterId.value)return; const r=await api.get(`/api/courses/by-department/${departmentFilterId.value}`); items.value=r.data }catch(e){errorMessage.value=err(e)} }
function selectForEdit(item){ selectedItem.value=item; updateForm.name=item.name; updateForm.code=item.code; updateForm.department_id=item.department_id; updateForm.credits=item.credits }
async function updateCourse(){ try{successMessage.value=''; errorMessage.value=''; const p={}; if(updateForm.name)p.name=updateForm.name; if(updateForm.code)p.code=updateForm.code; if(updateForm.department_id)p.department_id=updateForm.department_id; if(updateForm.credits!==''&&updateForm.credits!==null)p.credits=updateForm.credits; await api.put(`/api/courses/${selectedItem.value.id}`, p); successMessage.value='Curso atualizado com sucesso.'; await listByDepartment() }catch(e){errorMessage.value=err(e)} }
onMounted(async()=>{try{await loadDepartments(); await listByDepartment()}catch(e){errorMessage.value=err(e)}})
</script>
