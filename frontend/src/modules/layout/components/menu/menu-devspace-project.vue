<template>
  <div class="devspace-project-section" :class="{ 'collapsed': collapsed }">
    <!-- Project Selector -->
    <div v-if="!collapsed" class="project-selector-container">
      <label class="project-label">Project</label>
      <el-select 
        v-model="activeProjectId" 
        :key="componentKey"
        placeholder="Select Project" 
        filterable 
        class="project-selector w-full"
        size="default"
      >
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
    </div>

    <!-- Collapsed: Show icon only -->
    <el-tooltip v-else content="Select Project" placement="right">
      <div class="project-icon-collapsed">
        <i class="ri-folder-line" />
      </div>
    </el-tooltip>

    <!-- New Project Button -->
    <el-button 
      v-if="!collapsed"
      class="new-project-btn w-full mt-2"
      plain
      size="small"
      @click="openNewProjectModal"
    >
      <i class="ri-folder-add-line mr-1" />
      New Project
    </el-button>

    <el-tooltip v-else content="New Project" placement="right">
      <el-button 
        class="new-project-btn-collapsed"
        plain
        size="small"
        @click="openNewProjectModal"
      >
        <i class="ri-folder-add-line" />
      </el-button>
    </el-tooltip>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
});

const store = useStore();

const activeProjectId = computed({
  get: () => store.getters['devspace/activeProjectId'],
  set: (val) => store.dispatch('devspace/setActiveProjectId', val),
});

const projects = computed(() => store.getters['devspace/projects'] || []);

// Compute a key that changes when the active project name changes to force re-render of label
const componentKey = computed(() => {
  const active = projects.value.find(p => p.id === activeProjectId.value);
  return active ? `${active.id}-${active.name}` : 'default';
});

const openNewProjectModal = () => {
  // Dispatch global event to open modal in DevtelLayout
  window.dispatchEvent(new CustomEvent('devspace:open-new-project-modal'));
};

// Initialize projects on mount if not already loaded
onMounted(() => {
  if (projects.value.length === 0) {
    store.dispatch('devspace/fetchProjects');
  }
});
</script>

<style lang="scss" scoped>
.devspace-project-section {
  padding: 8px 0;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);

  &.collapsed {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
}

.project-selector-container {
  margin-bottom: 4px;
}

.project-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.project-selector {
  :deep(.el-input__wrapper) {
    background-color: #000000;
    border: 1px solid #3f3f46;
    box-shadow: none;
    transition: all 0.2s ease;
    
    &:hover {
      background-color: #09090b;
      border-color: #52525b;
    }
    
    &.is-focus {
      background-color: #09090b;
      border-color: #71717a;
      box-shadow: 0 0 0 1px rgba(113, 113, 122, 0.2);
    }
  }
  
  :deep(.el-input__inner) {
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
  }
  
  :deep(.el-input__suffix) {
    color: #a1a1aa;
  }
}

// Dropdown menu styling
:deep(.el-select-dropdown) {
  background-color: #000000 !important;
  border: 1px solid #3f3f46 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}

:deep(.el-select-dropdown__item) {
  background-color: #000000 !important;
  color: #ffffff !important;
  
  &:hover {
    background-color: #18181b !important;
  }
  
  &.is-selected {
    background-color: #27272a !important;
    color: #ffffff !important;
    font-weight: 600;
  }
}

.new-project-btn {
  background-color: transparent !important;
  border: 1px dashed rgba(255, 255, 255, 0.15) !important;
  color: rgba(255, 255, 255, 0.7) !important;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    color: rgba(255, 255, 255, 0.9) !important;
  }
}

.project-icon-collapsed {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.08);
  }
  
  i {
    font-size: 16px;
  }
}

.new-project-btn-collapsed {
  width: 32px !important;
  height: 32px !important;
  padding: 0 !important;
  background-color: transparent !important;
  border: 1px dashed rgba(255, 255, 255, 0.15) !important;
  color: rgba(255, 255, 255, 0.7) !important;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
  }
}
</style>
