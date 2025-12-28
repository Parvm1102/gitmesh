<template>
  <article class="flex items-start w-full group/input">
    <div class="flex flex-grow items-start w-full">
      <app-form-item
        :validation="$v.emails"
        :error-messages="{
          email: 'INVALID_ID',
        }"
        class="!mb-0 mr-0 flex-grow w-full terminal-input-group"
      >
        <el-input
          v-model="model.emails[0]"
          :placeholder="placeholder"
          class="terminal-merged-input"
          @blur="$v.emails.$touch"
          @change="$v.emails.$touch"
        >
          <template #append>
            <div class="flex items-center h-full">
              <el-select
                v-model="model.roles[0]"
                class="w-28 terminal-select"
                placeholder="LEVEL"
                placement="bottom-end"
                popper-class="terminal-select-dropdown"
              >
                <el-option
                  v-for="option in roles"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <div class="w-1.5 h-full bg-zinc-900 border-l border-zinc-800 hidden sm:block"></div>
            </div>
          </template>
        </el-input>
      </app-form-item>
    </div>
    <slot name="after" />
  </article>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps } from 'vue';
import { required, email } from '@vuelidate/validators';
import useVuelidate from '@vuelidate/core';
import AppFormItem from '@/shared/form/form-item.vue';
import { RoleEnum } from '@/modules/user/types/Roles';

type InvitedUser = {
  emails: string[],
  roles: string[]
}

const roles = [
  {
    value: RoleEnum.ADMIN,
    label: 'ADMIN_ACCESS',
  },
  {
    value: RoleEnum.READONLY,
    label: 'QUERY_ONLY',
  },
];

const emit = defineEmits<{(e: 'update:modelValue', value: InvitedUser): void}>();
const props = defineProps<{
  modelValue: InvitedUser,
  placeholder?: string,
}>();

const rules = {
  emails: { email },
  roles: { required },
};

const model = computed({
  get() {
    return props.modelValue;
  },
  set(value: InvitedUser) {
    emit('update:modelValue', value);
  },
});

const $v = useVuelidate(rules, model);
</script>

<style scoped>
/* 1. Monolithic Container Styling */
:deep(.terminal-merged-input .el-input__wrapper) {
  background-color: #09090b !important; /* zinc-950 */
  box-shadow: none !important;
  border: 1px solid #18181b !important; /* zinc-900 */
  border-right: none !important;
  border-radius: 0;
  height: 42px;
  padding-left: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.terminal-merged-input:hover .el-input__wrapper) {
  border-color: #27272a !important; /* zinc-800 */
}

:deep(.terminal-merged-input .el-input__wrapper.is-focus) {
  border-color: #ea580c !important; /* orange-600 */
  background-color: #000000 !important;
  z-index: 5;
}

:deep(.terminal-merged-input .el-input__inner) {
  color: #ffffff !important;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  letter-spacing: -0.01em;
}

:deep(.terminal-merged-input .el-input__inner::placeholder) {
  color: #3f3f46;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.1em;
}

/* 2. Integrated Select Module Styling */
:deep(.terminal-merged-input .el-input-group__append) {
  background-color: #09090b !important;
  box-shadow: none !important;
  border: 1px solid #18181b !important;
  border-left: 1px solid #18181b !important;
  border-radius: 0;
  padding: 0;
  transition: all 0.3s ease;
}

:deep(.terminal-merged-input:hover .el-input-group__append) {
  border-color: #27272a !important;
}

:deep(.terminal-select .el-input__wrapper) {
  box-shadow: none !important;
  background-color: transparent !important;
  padding: 0 12px;
  height: 100%;
}

:deep(.terminal-select .el-input__inner) {
  color: #71717a !important; /* zinc-400 */
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
}

:deep(.terminal-select .el-input__inner:hover) {
  color: #ea580c !important;
}

/* 3. Error Protocol Overlay */
:deep(.is-error .el-input__wrapper),
:deep(.is-error .el-input-group__append) {
  border-color: #ef4444 !important; /* red-500 */
  background-color: #450a0a05 !important;
}
</style>

<style>
/* 4. Global Dropdown Override */
.terminal-select-dropdown.el-popper {
  background-color: #09090b !important;
  border: 1px solid #18181b !important;
  border-radius: 0 !important;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.7) !important;
}

.terminal-select-dropdown .el-select-dropdown__item {
  color: #52525b !important; /* zinc-600 */
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 10px !important;
  height: 36px;
  line-height: 36px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0 16px !important;
}

.terminal-select-dropdown .el-select-dropdown__item.hover, 
.terminal-select-dropdown .el-select-dropdown__item:hover {
  background-color: #18181b !important; /* zinc-900 */
  color: #ffffff !important;
}

.terminal-select-dropdown .el-select-dropdown__item.selected {
  color: #ea580c !important;
  background-color: #ea580c05 !important;
}

.terminal-select-dropdown .el-popper__arrow {
  display: none !important;
}
</style>