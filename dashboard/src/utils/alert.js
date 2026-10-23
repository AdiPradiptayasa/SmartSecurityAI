import Swal from "sweetalert2";

const baseConfig = {
  background: "#0f172a",      // slate-900, senada dashboard
  color: "#e2e8f0",           // slate-200
  confirmButtonColor: "#dc2626",  // red-600, untuk aksi delete
  cancelButtonColor: "#334155",   // slate-700
  customClass: {
    popup: "rounded-2xl border border-slate-800",
  },
};

export function confirmDelete({ title, text, confirmText = "Ya, Hapus" }) {
  return Swal.fire({
    ...baseConfig,
    title,
    text,
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: confirmText,
    cancelButtonText: "Batal",
    reverseButtons: true,
  });
}

export function showSuccess(title, text = "") {
  return Swal.fire({
    ...baseConfig,
    title,
    text,
    icon: "success",
    confirmButtonColor: "#2563eb", // blue-600
    timer: 2000,
    timerProgressBar: true,
    showConfirmButton: false,
  });
}

export function showError(title, text = "") {
  return Swal.fire({
    ...baseConfig,
    title,
    text,
    icon: "error",
    confirmButtonColor: "#dc2626",
  });
}