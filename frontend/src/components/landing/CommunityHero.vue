<template>
  <section class="max-w-6xl mx-auto px-6 py-24">
    <div class="max-w-3xl">
      <!-- Title -->
      <h1 class="text-white font-sans text-5xl md:text-6xl font-black leading-tight tracking-tight">
        GitMesh
        <span class="block text-xl md:text-2xl font-medium text-white/70 mt-2">
          Community Edition
        </span>
      </h1>

      <!-- Description -->
      <p class="mt-8 text-lg text-white/80 leading-relaxed">
        GitMesh is an open-source platform for building and operating
        decentralized trust infrastructure.
      </p>

      <p class="mt-4 text-base text-white/70 leading-relaxed">
        The Community Edition is developed and maintained by contributors from
        multiple open-source organizations under the Linux Foundation
        Decentralized Trust Lab.
      </p>

      <p class="mt-4 text-base text-white/70 leading-relaxed">
        The Enterprise Edition is officially provided and supported by
        <span class="text-orange-500 font-medium">
          <a href="https://alveoli.app/" target="_blank" rel="noopener noreferrer">
            Alveoli
          </a>
        </span>.
      </p>

      <!-- CTAs -->
      <div class="mt-12 flex flex-wrap gap-4">
        <router-link
          to="/auth/signup"
          class="bg-orange-500 text-black px-8 py-3 font-mono text-sm font-semibold
                 hover:bg-orange-400 transition-colors"
        >
          Get Started
        </router-link>

        <router-link
          to="/auth/signin"
          class="border border-white text-white px-8 py-3 font-mono text-sm font-semibold
                 hover:bg-white hover:text-black transition-colors"
        >
          Sign In
        </router-link>
      </div>
    </div>

    <!-- Principles -->
    <div class="mt-24 grid grid-cols-1 md:grid-cols-3 gap-10">
      <div>
        <h3 class="font-mono text-base font-semibold text-white mb-2">
          Open Governance
        </h3>
        <p class="text-sm text-white/70 leading-relaxed">
          Developed in the open with transparent governance and community-driven
          decision making.
        </p>
      </div>

      <div>
        <h3 class="font-mono text-base font-semibold text-white mb-2">
          Local & Self-Hosted
        </h3>
        <p class="text-sm text-white/70 leading-relaxed">
          Runs locally using your own infrastructure, APIs, and credentials.
          Your data stays under your control.
        </p>
      </div>

      <div>
        <h3 class="font-mono text-base font-semibold text-white mb-2">
          Apache 2.0 Licensed
        </h3>
        <p class="text-sm text-white/70 leading-relaxed">
          Permissive open-source licensing that enables modification,
          redistribution, and commercial use.
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
</script>
