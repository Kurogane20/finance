<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAccountingStore } from '../stores/accounting';
import { useRouter } from 'vue-router';

const accountingStore = useAccountingStore();
const router = useRouter();

const form = ref({
  date: new Date().toISOString().split('T')[0],
  description: '',
  reference: '',
  posted: false,
  items: [
    { account_id: '', debit: 0, credit: 0 },
    { account_id: '', debit: 0, credit: 0 }
  ]
});

const isSubmitting = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Computed Totals
const totalDebit = computed(() => {
  return form.value.items.reduce((sum, item) => sum + Number(item.debit || 0), 0);
});

const totalCredit = computed(() => {
  return form.value.items.reduce((sum, item) => sum + Number(item.credit || 0), 0);
});

const isBalanced = computed(() => {
  return Math.abs(totalDebit.value - totalCredit.value) < 0.01 && totalDebit.value > 0;
});

const balanceDifference = computed(() => {
    return totalDebit.value - totalCredit.value;
});

// Actions
const addRow = () => {
  form.value.items.push({ account_id: '', debit: 0, credit: 0 });
};

const removeRow = (index) => {
  if (form.value.items.length > 2) {
    form.value.items.splice(index, 1);
  }
};

const submitJournal = async () => {
  if (!isBalanced.value) {
    errorMessage.value = 'Entries must be balanced!';
    return;
  }
  
  // Validate that all rows have an account
  if (form.value.items.some(item => !item.account_id)) {
     errorMessage.value = 'All rows must have an account selected.';
     return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
     const payload = {
        ...form.value,
        date: new Date(form.value.date).toISOString()
     };
     
     await accountingStore.createJournalEntry(payload);
     
     successMessage.value = 'Journal Entry successfully posted.';
     
     // Reset form
     form.value = {
        date: new Date().toISOString().split('T')[0],
        description: '',
        reference: '',
        posted: false,
        items: [
            { account_id: '', debit: 0, credit: 0 },
            { account_id: '', debit: 0, credit: 0 }
        ]
     };
  } catch (err) {
      errorMessage.value = err.response?.data?.detail || 'Failed to submit journal entry.'
  } finally {
      isSubmitting.value = false;
  }
};

onMounted(() => {
  accountingStore.fetchAccounts();
});
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <div class="page-header flex justify-between items-center">
      <div>
        <h1 class="page-title">General Journal</h1>
        <p class="page-subtitle">Record new double-entry transactions</p>
      </div>
    </div>

    <div v-if="successMessage" class="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-md flex items-center gap-2">
      <span class="text-xl">✅</span> {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-center gap-2">
      <span class="text-xl">⚠️</span> {{ errorMessage }}
    </div>

    <div class="card">
      <div class="card-header bg-slate-50">
        <h3 class="font-semibold text-slate-800">New Journal Entry</h3>
      </div>
      
      <div class="card-body">
         <!-- Header Fields -->
         <div class="grid grid-cols-1 md:grid-cols-12 gap-6 mb-8">
            <div class="md:col-span-3">
               <label class="form-label">Date</label>
               <input v-model="form.date" type="date" class="form-input">
            </div>
            <div class="md:col-span-3">
                <label class="form-label">Reference No.</label>
                <input v-model="form.reference" type="text" class="form-input" placeholder="e.g. JV-2024-001">
            </div>
            <div class="md:col-span-6">
                 <label class="form-label">Description / Memo</label>
                 <input v-model="form.description" type="text" class="form-input" placeholder="Description of the transaction">
            </div>
         </div>

         <!-- Lines -->
         <div class="mb-8">
            <div class="overflow-hidden border rounded-lg border-slate-200">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
                        <tr>
                            <th class="px-4 py-3 text-left w-5/12">Account</th>
                            <th class="px-4 py-3 text-right w-3/12">Debit</th>
                            <th class="px-4 py-3 text-right w-3/12">Credit</th>
                            <th class="px-2 py-3 w-1/12"></th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-slate-200">
                        <tr v-for="(item, index) in form.items" :key="index">
                            <td class="px-4 py-2">
                                <select v-model="item.account_id" class="form-input py-1.5 text-sm">
                                    <option value="" disabled>Select Account</option>
                                    <option v-for="acc in accountingStore.flattenedAccounts" :key="acc.value" :value="acc.value">
                                        {{ acc.label }}
                                    </option>
                                </select>
                            </td>
                            <td class="px-4 py-2">
                                <input v-model.number="item.debit" type="number" step="0.01" min="0" 
                                    :disabled="item.credit > 0"
                                    class="form-input text-right py-1.5 text-sm disabled:bg-slate-50 disabled:text-slate-400">
                            </td>
                            <td class="px-4 py-2">
                                <input v-model.number="item.credit" type="number" step="0.01" min="0" 
                                    :disabled="item.debit > 0"
                                    class="form-input text-right py-1.5 text-sm disabled:bg-slate-50 disabled:text-slate-400">
                            </td>
                            <td class="px-2 py-2 text-center">
                                <button @click="removeRow(index)" class="text-slate-400 hover:text-red-500 transition-colors" title="Remove line">
                                    ✕
                                </button>
                            </td>
                        </tr>
                    </tbody>
                    <tfoot class="bg-slate-50 font-semibold text-slate-700">
                        <tr>
                            <td class="px-4 py-3 text-right text-sm uppercase">Total</td>
                            <td class="px-4 py-3 text-right font-mono" :class="{'text-green-600': isBalanced, 'text-red-600': !isBalanced}">
                                {{ totalDebit.toLocaleString('id-ID', { minimumFractionDigits: 2 }) }}
                            </td>
                            <td class="px-4 py-3 text-right font-mono" :class="{'text-green-600': isBalanced, 'text-red-600': !isBalanced}">
                                {{ totalCredit.toLocaleString('id-ID', { minimumFractionDigits: 2 }) }}
                            </td>
                            <td></td>
                        </tr>
                        <tr v-if="!isBalanced" class="bg-red-50">
                            <td colspan="4" class="px-4 py-2 text-right text-xs text-red-600 italic">
                                Out of Balance by {{ Math.abs(balanceDifference).toLocaleString('id-ID', { minimumFractionDigits: 2 }) }}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <button @click="addRow" class="mt-3 text-sm text-blue-600 font-medium hover:text-blue-800 flex items-center gap-1">
                <span>+</span> Add Another Line
            </button>
         </div>
         
         <!-- Actions -->
         <div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button type="button" class="btn btn-secondary" @click="router.back()">Cancel</button>
            <button 
                type="button" 
                class="btn btn-primary min-w-[150px]"
                :disabled="!isBalanced || isSubmitting"
                @click="submitJournal"
            >
                {{ isSubmitting ? 'Posting...' : 'Post Journal' }}
            </button>
         </div>

      </div>
    </div>
  </div>
</template>
