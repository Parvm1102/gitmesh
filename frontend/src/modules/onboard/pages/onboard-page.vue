<template>
  <div class="min-h-screen bg-black flex flex-col relative selection:bg-orange-500/30 overflow-x-hidden">
    
    <div class="fixed inset-0 bg-[linear-gradient(to_right,#27272a_1px,transparent_1px),linear-gradient(to_bottom,#27272a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-20 pointer-events-none"></div>

    <div class="relative z-10 flex-1 flex flex-col pb-32"> 
      
      <div class="mt-12 mb-10 flex justify-center px-6">
        <div class="flex flex-col items-center gap-6 w-full max-w-2xl text-center">
          
          <div class="relative group cursor-default">
            <div class="flex items-center justify-center gap-3">
              <div class="h-[1px] w-6 bg-zinc-800 group-hover:w-10 group-hover:bg-orange-500 transition-all duration-500"></div>
              <span class="text-white font-sans text-xl font-black tracking-[0.2em] uppercase italic">
                Git<span class="text-orange-500">Mesh</span>
              </span>
              <div class="h-[1px] w-6 bg-zinc-800 group-hover:w-10 group-hover:bg-orange-500 transition-all duration-500"></div>
            </div>
          </div>

          <div class="inline-flex items-stretch border border-zinc-800 bg-zinc-950 shadow-[0_0_15px_rgba(0,0,0,0.5)] overflow-hidden">
              <div class="px-2 py-1 bg-zinc-900 border-r border-zinc-800 flex items-center">
                <span class="text-zinc-500 font-mono text-[9px] uppercase tracking-tighter">Session</span>
              </div>
              <div class="px-4 py-2 flex items-center gap-2">
                  <span class="text-zinc-200 font-mono text-[11px] tracking-tight italic font-bold">
                    root@{{ currentUser?.firstName?.toLowerCase() || 'user' }}
                  </span>
                  <span class="text-zinc-600 font-mono text-[11px]">:</span>
                  <span class="text-orange-500 font-mono text-[11px] font-bold">./setup_workspace.sh</span>
              </div>
          </div>
        </div>
      </div>

      <div class="sticky top-0 z-20 bg-black/80 backdrop-blur-md border-y border-zinc-900 py-3 flex justify-center px-6">
        <div class="flex items-center w-full max-w-2xl justify-between overflow-x-auto no-scrollbar">
          
          <div
            v-for="(step, index) in Object.values(onboardingSteps)"
            :key="step.name"
            class="flex items-center flex-1 group"
            :class="[
              index < currentStep - 1 ? 'cursor-pointer' : 'cursor-default',
              index !== Object.values(onboardingSteps).length - 1 ? 'w-full' : ''
            ]"
            @click="onStepClick(index)"
          >
            <div class="flex flex-col gap-1 transition-all duration-300">
              <span 
                class="font-mono text-[9px] uppercase tracking-widest"
                :class="getStepColor(index + 1)"
              >
                Phase_0{{ index + 1 }}
              </span>
              <span 
                class="font-mono text-[10px] font-bold uppercase tracking-tighter"
                :class="index + 1 === currentStep ? 'text-white' : 'text-zinc-600'"
              >
                {{ step.name }}
              </span>
            </div>

            <div 
              v-if="index !== Object.values(onboardingSteps).length - 1"
              class="h-[1px] flex-1 mx-4 bg-zinc-900 relative overflow-hidden"
            >
              <div 
                v-if="index + 1 < currentStep" 
                class="absolute inset-0 bg-orange-500/30 transition-all duration-500"
              ></div>
            </div>
          </div>

        </div>
      </div>

      <div class="flex justify-center mt-12 px-6">
        <main class="w-full max-w-2xl relative">
          <div class="absolute -top-4 -left-4 w-8 h-8 border-t border-l border-zinc-800"></div>
          
          <div class="text-zinc-300 font-mono bg-zinc-950/50 border border-zinc-900 p-8 shadow-2xl">
            <component
              :is="stepConfig.component"
              v-model="form"
              @allow-redirect="onConnect"
              @invite-colleagues="onInviteColleagues"
            />
          </div>

          <div class="absolute -bottom-4 -right-4 w-8 h-8 border-b border-r border-zinc-800"></div>
        </main>
      </div>

    </div>

    <div class="fixed bottom-0 w-full bg-black border-t border-zinc-900 py-6 px-6 z-30 flex justify-center shadow-[0_-20px_50px_rgba(0,0,0,0.8)]">
      <div class="w-full max-w-2xl">
        <el-tooltip
          placement="top"
          :disabled="!stepConfig.ctaTooltip || !$v.$invalid"
          :content="stepConfig.ctaTooltip"
          popper-class="terminal-tooltip" 
        >
          <div class="w-full">
            <button
              class="group w-full h-14 bg-orange-600 hover:bg-orange-500 disabled:bg-zinc-900 disabled:text-zinc-700 disabled:cursor-not-allowed text-black font-mono text-xs font-black transition-all flex items-center justify-center gap-3 uppercase tracking-[0.3em] relative overflow-hidden shadow-[0_0_20px_rgba(234,88,12,0.1)]"
              :disabled="$v.$invalid || loadingSubmitAction"
              @click="onBtnClick"
            >
              <div class="absolute inset-0 w-full h-full bg-white/10 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
              
              <span v-if="loadingSubmitAction" class="animate-spin w-4 h-4 border-2 border-black border-t-transparent rounded-full"></span>
              <span v-else class="flex items-center gap-3 relative z-10">
                 EXECUTE_PHASE_{{ currentStep }} :: {{ stepConfig.cta }} <i class="ri-arrow-right-line text-lg group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
          </div>
        </el-tooltip>
        
        <div class="mt-3 flex justify-between items-center px-1">
           <span class="text-[8px] font-mono text-zinc-600 uppercase tracking-widest italic">System_Ready // Waiting for directive</span>
           <span class="text-[8px] font-mono text-zinc-600 uppercase tracking-widest">GitMesh Cloud Infrastructure</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import {
  reactive, ref, computed, watch, onUnmounted,
} from 'vue';
import {
  mapGetters,
} from '@/shared/vuex/vuex.helpers';
import onboardingSteps from '@/modules/onboard/config/steps';
import useVuelidate from '@vuelidate/core';
import { useStore } from 'vuex';
import { GitmeshIntegrations } from '@/integrations/integrations-config';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useStore();

const { currentUser, currentTenant } = mapGetters('auth');

const loadingSubmitAction = ref(false);
const allowRedirect = ref(false);
const currentStep = ref(1);
const form = reactive({
  tenantName: currentTenant.value?.name,
  activeIntegrations: 0,
  invitedUsers: [{
    emails: [],
    roles: ['admin'],
  }],
});

const stepConfig = computed(() => Object.values(onboardingSteps)[currentStep.value - 1]);
const activeIntegrations = computed(() => GitmeshIntegrations.mappedEnabledConfigs(
  store,
).filter((integration) => integration.status));

const getStepColor = (stepIndex: number) => {
  if (stepIndex === currentStep.value) return 'text-orange-500';
  if (stepIndex < currentStep.value) return 'text-zinc-500 line-through decoration-orange-500/40';
  return 'text-zinc-700';
};

const preventWindowReload = (e: BeforeUnloadEvent) => {
  if (!allowRedirect.value) {
    e.preventDefault();
    e.returnValue = '';
  } else {
    allowRedirect.value = false;
  }
};

window.addEventListener('beforeunload', preventWindowReload);

onUnmounted(() => {
  window.removeEventListener('beforeunload', preventWindowReload);
});

watch(currentTenant, (tenant, oldTenant) => {
  const params = new URLSearchParams(window.location.search);
  const code = params.get('code');

  if (tenant?.id === oldTenant?.id) return;

  if (tenant) {
    form.tenantName = tenant.name;
    store.dispatch('integration/doFetch');
    currentStep.value = 2;
  } else if (code) {
    router.replace({ query: {} });
  }
}, { deep: true, immediate: true });

watch(activeIntegrations, (integrations) => {
  form.activeIntegrations = integrations.length;
  if (integrations.length && currentStep.value < 2) {
    currentStep.value = 2;
  }
});

const $v = useVuelidate({}, form);

const onBtnClick = () => {
  loadingSubmitAction.value = true;
  if (currentStep.value === 3) allowRedirect.value = true;

  stepConfig.value.submitAction(form, activeIntegrations.value).then(() => {
    if (currentStep.value < Object.values(onboardingSteps).length) {
      currentStep.value += 1;
    }
  }).finally(() => {
    loadingSubmitAction.value = false;
  });
};

const onStepClick = (index: number) => {
  if (!(index < currentStep.value - 1)) return;
  currentStep.value = index + 1;
};

const onConnect = (val: boolean) => { allowRedirect.value = val; };
const onInviteColleagues = () => { currentStep.value = 3; };
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;600;700;900&display=swap');

.font-sans { font-family: 'Inter', sans-serif; }
.font-mono { font-family: 'JetBrains Mono', monospace; }

@keyframes shimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

:global(.terminal-tooltip) {
    background-color: #09090b !important;
    border: 1px solid #18181b !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    border-radius: 0px !important;
    padding: 8px 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
</style>