# PowerShell script to create comprehensive directory structure for integrated cognitive architecture
$basePath = "c:/dix_vision_v42.2"

# INDIRA cognitive structure
$indiraDirs = @(
    "indira_cognitive/indira_mind/self_awareness",
    "indira_cognitive/indira_mind/identity",
    "indira_cognitive/indira_mind/capabilities",
    "indira_cognitive/indira_mind/performance",
    "indira_cognitive/indira_mind/mental_state",
    "indira_cognitive/indira_mind/maturity",
    "indira_cognitive/indira_brain/reasoning",
    "indira_cognitive/indira_brain/memory",
    "indira_cognitive/indira_brain/knowledge",
    "indira_cognitive/indira_brain/learning",
    "indira_cognitive/indira_brain/execution",
    "indira_cognitive/indira_brain/analysis",
    "indira_cognitive/indira_brain/plugins",
    "indira_cognitive/indira_brain/interfaces"
)

# DYON cognitive structure
$dyonDirs = @(
    "dyon_cognitive/dyon_mind/reflection",
    "dyon_cognitive/dyon_brain/simulation",
    "dyon_cognitive/dyon_brain/debugging",
    "dyon_cognitive/dyon_brain/knowledge",
    "dyon_cognitive/dyon_brain/plugins",
    "dyon_cognitive/dyon_brain/interfaces"
)

# Coordination layer
$coordinationDirs = @(
    "coordination_layer/governance",
    "coordination_layer/shared_mental_models",
    "coordination_layer/resource_allocation",
    "coordination_layer/shared_infrastructure"
)

# Shared infrastructure
$sharedDirs = @(
    "shared_infrastructure/unified_memory",
    "shared_infrastructure/event_bus",
    "shared_infrastructure/vector_database",
    "shared_infrastructure/knowledge_graph",
    "shared_infrastructure/llm_infrastructure",
    "shared_infrastructure/learning_infrastructure",
    "shared_infrastructure/monitoring",
    "shared_infrastructure/api_layer"
)

# Create all directories
$allDirs = $indiraDirs + $dyonDirs + $coordinationDirs + $sharedDirs

foreach ($dir in $allDirs) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    Write-Host "Created: $fullPath"
}

Write-Host "Directory structure creation complete!"