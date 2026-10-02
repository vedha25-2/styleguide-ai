/**
 * StyleGuide AI - Wardrobe Management & Filtering Script
 */

const SUBCATEGORIES_MAP = {
  'Clothes': ['Tops', 'Shirts', 'T-shirts', 'Jeans', 'Trousers', 'Skirts', 'Dresses', 'Kurtis', 'Sarees', 'Jackets', 'Other'],
  'Jewellery': ['Necklace', 'Earrings', 'Bracelet', 'Ring', 'Watch', 'Other'],
  'Footwear': ['Sneakers', 'Heels', 'Sandals', 'Flats', 'Boots', 'Shoes', 'Other'],
  'Accessories': ['Handbags', 'Sunglasses', 'Belts', 'Scarves', 'Other']
};

document.addEventListener('DOMContentLoaded', () => {
  // Main Category -> Subcategory Dropdown dynamic population
  const mainCatSelect = document.getElementById('mainCategorySelect');
  const subCatSelect = document.getElementById('subCategorySelect');

  if (mainCatSelect && subCatSelect) {
    function updateSubcategories(selectedCategory) {
      const options = SUBCATEGORIES_MAP[selectedCategory] || ['Other'];
      subCatSelect.innerHTML = '';
      options.forEach(sub => {
        const opt = document.createElement('option');
        opt.value = sub;
        opt.textContent = sub;
        subCatSelect.appendChild(opt);
      });
    }

    mainCatSelect.addEventListener('change', (e) => {
      updateSubcategories(e.target.value);
    });

    // Initial populate if subcategory is empty
    if (subCatSelect.children.length === 0) {
      updateSubcategories(mainCatSelect.value);
    }
  }

  // Client-side Wardrobe Filtering
  const filterBtns = document.querySelectorAll('.wardrobe-filter-btn');
  const searchInput = document.getElementById('wardrobeSearchInput');
  const itemCards = document.querySelectorAll('.wardrobe-item-col');

  let currentCategory = 'all';
  let currentSearch = '';

  function applyWardrobeFilters() {
    itemCards.forEach(col => {
      const cat = col.getAttribute('data-category') || '';
      const text = (col.innerText || '').toLowerCase();

      const matchesCat = (currentCategory === 'all' || cat.toLowerCase() === currentCategory.toLowerCase());
      const matchesSearch = (!currentSearch || text.includes(currentSearch));

      if (matchesCat && matchesSearch) {
        col.style.display = '';
      } else {
        col.style.display = 'none';
      }
    });

    const visibleCount = Array.from(itemCards).filter(c => c.style.display !== 'none').length;
    const noItemsNotice = document.getElementById('noItemsNotice');
    if (noItemsNotice) {
      noItemsNotice.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      filterBtns.forEach(b => b.classList.remove('active', 'btn-primary-gradient'));
      filterBtns.forEach(b => b.classList.add('btn-outline-gradient'));
      this.classList.remove('btn-outline-gradient');
      this.classList.add('active', 'btn-primary-gradient');

      currentCategory = this.getAttribute('data-filter') || 'all';
      applyWardrobeFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim().toLowerCase();
      applyWardrobeFilters();
    });
  }

  // Favorite Button AJAX Handler
  document.querySelectorAll('.ajax-fav-btn').forEach(btn => {
    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      e.stopPropagation();

      const itemType = this.getAttribute('data-type') || 'item';
      const itemId = this.getAttribute('data-id');

      try {
        const resp = await fetch('/favorites/toggle', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({ item_type: itemType, id: itemId })
        });
        const data = await resp.json();

        if (data.success) {
          if (data.is_favorite) {
            this.classList.add('active');
            this.innerHTML = '<i class="fa-solid fa-heart text-danger"></i>';
          } else {
            this.classList.remove('active');
            this.innerHTML = '<i class="fa-regular fa-heart"></i>';
          }
        }
      } catch (err) {
        console.error('Failed to toggle favorite:', err);
      }
    });
  });
});
