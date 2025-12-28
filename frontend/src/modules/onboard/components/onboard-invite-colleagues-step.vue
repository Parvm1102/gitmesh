<template>
  <div class="pt-2">
    <div class="flex items-center gap-2 mb-4 px-1">
       <span class="h-1 w-1 bg-orange-600"></span>
       <span class="text-[9px] font-mono text-zinc-500 uppercase tracking-[0.2em]">Deployment_Target: Core_Team</span>
    </div>

    <app-form-item
      :validation="$v.invitedUsers"
      class="terminal-form-item !mb-0"
    >
      <template #label>
        <div class="flex items-center justify-between mb-2">
           <span class="text-zinc-200 font-mono text-[10px] uppercase tracking-[0.2em] font-black italic">
            > Access_Control_List
          </span>
          <span class="text-zinc-700 font-mono text-[8px] uppercase tracking-widest">
            Count: 0{{ form.invitedUsers.length }}
          </span>
        </div>
      </template>

      <div class="flex flex-col gap-3">
        <div 
          v-for="(_, ii) of form.invitedUsers"
          :key="ii"
          class="group flex gap-2 items-stretch animate-in fade-in slide-in-from-left-2 duration-300"
        >
          <div class="flex flex-col justify-center items-center w-8 bg-zinc-900 border border-zinc-800 transition-colors group-hover:border-zinc-700">
             <span class="text-[9px] font-mono text-zinc-600 group-hover:text-zinc-400">#0{{ ii + 1 }}</span>
          </div>

          <div class="flex-grow">
            <app-onboard-user-array-input
              v-model="form.invitedUsers[ii]"
              placeholder="IDENTIFY_USER@DOMAIN.COM"
            />
          </div>

          <button
            v-if="form.invitedUsers.length > 1"
            class="w-10 flex items-center justify-center border border-zinc-800 bg-zinc-950 hover:bg-red-500/10 hover:border-red-500 text-zinc-600 hover:text-red-500 transition-all shrink-0"
            @click="removeUser(ii)"
            type="button"
            title="Terminate Link"
          >
            <i class="ri-close-line text-lg" />
          </button>
        </div>
      </div>
    </app-form-item>

    <div class="mt-6 flex justify-center">
      <button 
        class="relative flex items-center gap-3 px-6 py-2 border border-dashed border-zinc-800 hover:border-orange-500/50 hover:bg-orange-500/[0.02] text-zinc-500 hover:text-orange-500 transition-all font-mono text-[10px] font-bold uppercase tracking-[0.2em] group overflow-hidden" 
        @click="addUser()"
        type="button"
      >
        <div class="absolute inset-0 bg-orange-500/5 -translate-x-full group-hover:translate-x-0 transition-transform duration-500"></div>
        
        <i class="ri-add-line text-sm relative z-10"></i>
        <span class="relative z-10">Provision_New_Seat</span>
      </button>
    </div>

    <div class="mt-8 flex items-center gap-2 opacity-20 select-none">
       <div class="h-[1px] flex-1 bg-zinc-700"></div>
       <span class="text-[7px] font-mono text-zinc-500 tracking-[0.4em] uppercase">Auth_Directive_Active</span>
       <div class="h-[1px] flex-1 bg-zinc-700"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppFormItem from '@/shared/form/form-item.vue';
import useVuelidate from '@vuelidate/core';
import AppOnboardUserArrayInput from '@/modules/onboard/components/onboard-user-array-input.vue';
import { RoleEnum } from '@/modules/user/types/Roles';

type Form = {
  invitedUsers: {
    emails: string[];
    roles: string[];
  }[]
}

const emit = defineEmits<{(e: 'update:modelValue', value: Form): void}>();
const props = defineProps<{
  modelValue: Form,
}>();

const form = computed<Form>({
  get() {
    return props.modelValue;
  },
  set(value: Form) {
    emit('update:modelValue', {
      ...props.modelValue,
      invitedUsers: value.invitedUsers,
    });
  },
});

const $v = useVuelidate({}, form);

const addUser = () => {
  form.value.invitedUsers.push({
    emails: [],
    roles: [RoleEnum.ADMIN],
  });
};

const removeUser = (index: number) => {
  form.value.invitedUsers.splice(index, 1);
};
</script>

<style scoped>
/* Keyframes for the entrance animation if you want to be extra precise */
.animate-in {
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-4px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>