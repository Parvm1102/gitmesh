<template>
  <div class="min-h-screen bg-black flex flex-col relative selection:bg-orange-500/30 overflow-x-hidden pb-24">
    
    <div class="fixed inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-20 pointer-events-none"></div>

    <div class="relative z-10 flex-1 flex flex-col">
      <div class="flex justify-center py-16 px-6">
        <div class="flex flex-col md:flex-row gap-6 items-center max-w-2xl w-full">
          <div class="relative shrink-0">
            <div class="w-16 h-16 bg-zinc-950 border border-zinc-800 flex items-center justify-center shadow-[0_0_30px_rgba(234,88,12,0.1)]">
               <i class="ri-pulse-line text-3xl text-orange-500 animate-pulse"></i>
            </div>
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-orange-600 animate-ping opacity-50"></div>
          </div>

          <div class="flex flex-col gap-1 text-center md:text-left">
            <span class="text-[10px] font-mono text-zinc-500 uppercase tracking-[0.4em] mb-1">Phase_Final // Deployment_Briefing</span>
            <p class="text-[11px] font-mono text-zinc-400 leading-relaxed uppercase tracking-tight">
              > Schedule a synchronization session with GitMesh Sales Team to optimize your environment.
            </p>
          </div>
        </div>
      </div>

      <div class="flex justify-center px-4 md:px-8 mb-12">
        <div class="w-full max-w-4xl border border-zinc-900 bg-zinc-950/50 relative p-1">
          <div class="absolute -top-[1px] -left-[1px] w-4 h-4 border-t border-l border-orange-600"></div>
          <div class="absolute -bottom-[1px] -right-[1px] w-4 h-4 border-b border-r border-orange-600"></div>
          
          <div id="embbeded-script" class="w-full min-h-[600px] bg-black/40" />
        </div>
      </div>
    </div>

    <div class="fixed bottom-0 w-full bg-black border-t border-zinc-900 flex justify-center py-6 px-8 z-50 shadow-[0_-20px_50px_rgba(0,0,0,0.8)]">
      <div class="w-full max-w-2xl">
        <button
          class="group w-full h-14 bg-orange-600 hover:bg-orange-500 text-black font-mono text-xs font-black transition-all flex items-center justify-center gap-3 uppercase tracking-[0.3em] relative overflow-hidden shadow-[0_0_20px_rgba(234,88,12,0.15)]"
          @click="onBtnClick"
        >
          <div class="absolute inset-0 bg-white/10 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
          
          <span class="flex items-center gap-3 relative z-10">
            INITIALIZE_WORKSPACE <i class="ri-arrow-right-line text-lg group-hover:translate-x-1 transition-transform" />
          </span>
        </button>
        
        <div class="mt-3 text-center">
           <span class="text-[8px] font-mono text-zinc-700 uppercase tracking-[0.3em]">
             Authorized_Link: Secure_Transmission_Channel_01
           </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { renderCal } from '@/utils/cals';

const router = useRouter();

onMounted(() => {
  renderCal({
    calLink: 'gitmesh/sales',
  });
});

const onBtnClick = () => {
  router.push({ name: 'welcomeaboard' });
};
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Inter:wght@400;900&display=swap');

.font-sans { font-family: 'Inter', sans-serif; }
.font-mono { font-family: 'JetBrains Mono', monospace; }

@keyframes shimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}

/* Customizing the Cal.com embed appearance slightly if it supports system styles */
#embbeded-script {
  mask-image: linear-gradient(to bottom, black 95%, transparent 100%);
}

.limit-width {
  @apply w-full;
  max-width: 42.75rem;
}
</style>